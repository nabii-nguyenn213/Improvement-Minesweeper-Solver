from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import numpy as np
import time
import os

# Your solver
from models.improvement_heuristic import Improvement_Heuristic

# ===== Constants =====
HIDDEN_CELL = -0.5
MINE_CELL = -2
FLAG_CELL = -1

HEADLESS = os.environ.get("HEADLESS", "0") in ("1", "true", "True")
PAGE_LOAD_TIMEOUT = 20

# ===== Utilities =====
def _norm_coords(coords):
    """
    Convert coords to a JSON-serializable list of [int, int] with native Python ints.
    Accepts sequences/np arrays of (r, c).
    """
    out = []
    if not coords:
        return out
    for rc in coords:
        r, c = rc[0], rc[1]
        out.append([int(r), int(c)])
    return out

# ===== JS-accelerated helpers =====
def js_get_board(driver, nrow, ncol):
    """
    Return np.ndarray of shape (nrow, ncol) with numeric states by reading
    all cell classes in a single JS call, then mapping locally in Python.
    """
    classes = driver.execute_script("""
        const rows = arguments[0], cols = arguments[1];
        const out = Array.from({length: rows}, (_, r) => {
          const row = [];
          for (let c = 1; c <= cols; c++) {
            const el = document.getElementById((r+1) + "_" + c);
            row.push(el ? el.className : "");
          }
          return row;
        });
        return out;
    """, int(nrow), int(ncol))

    board = np.empty((nrow, ncol), dtype=float)
    for r in range(nrow):
        for c in range(ncol):
            cls = (classes[r][c] or "")
            if cls == "square bombflagged":
                board[r, c] = FLAG_CELL
            elif cls == "square blank":
                board[r, c] = HIDDEN_CELL
            elif "bombdeath" in cls:
                board[r, c] = MINE_CELL
            elif "open" in cls:
                # robust parse for open0..open8
                val = None
                for d in "012345678":
                    if ("open" + d) in cls:
                        val = float(d)
                        break
                board[r, c] = 0.0 if val is None else val
            else:
                board[r, c] = HIDDEN_CELL
    return board

def js_left_click_cells(driver, coords):
    """Dispatch real-looking left-clicks (mousedown+mouseup+click) at cell centers in one JS call."""
    coords = _norm_coords(coords)
    if not coords:
        return
    driver.execute_script("""
        const coords = arguments[0];
        function leftClick(el){
            const r = el.getBoundingClientRect();
            const cx = r.left + r.width/2;
            const cy = r.top + r.height/2;
            const base = {bubbles:true, cancelable:true, composed:true,
                          clientX: cx, clientY: cy,
                          screenX: window.screenX + cx, screenY: window.screenY + cy,
                          pageX: window.scrollX + cx, pageY: window.scrollY + cy,
                          button: 0, buttons: 1};
            el.dispatchEvent(new MouseEvent('mousedown', base));
            el.dispatchEvent(new MouseEvent('mouseup', base));
            el.dispatchEvent(new MouseEvent('click', base));
        }
        for (const [r, c] of coords){
            const el = document.getElementById((r+1) + "_" + (c+1));
            if (el) leftClick(el);
        }
    """, coords)

def js_rightflag_cells(driver, coords):
    """Dispatch real-looking right-clicks (flag) in one JS call (optional; off by default to save time)."""
    coords = _norm_coords(coords)
    if not coords:
        return
    driver.execute_script("""
        const coords = arguments[0];
        function rightClick(el){
            const r = el.getBoundingClientRect();
            const cx = r.left + r.width/2;
            const cy = r.top + r.height/2;
            const base = {bubbles:true, cancelable:true, composed:true,
                          clientX: cx, clientY: cy,
                          screenX: window.screenX + cx, screenY: window.screenY + cy,
                          pageX: window.scrollX + cx, pageY: window.scrollY + cy,
                          button: 2, buttons: 2};
            el.dispatchEvent(new MouseEvent('mousedown', base));
            el.dispatchEvent(new MouseEvent('contextmenu', base));
            el.dispatchEvent(new MouseEvent('mouseup', base));
        }
        for (const [r, c] of coords){
            const el = document.getElementById((r+1) + "_" + (c+1));
            if (el) rightClick(el);
        }
    """, coords)

def js_face_class(driver):
    return driver.execute_script("return document.getElementById('face')?.className || '';")

def reset_board(driver):
    """Click the face with realistic mouse events to start a new game (no sleeps)."""
    driver.execute_script("""
        const f = document.getElementById('face');
        if (!f) return;
        const r = f.getBoundingClientRect();
        const cx = r.left + r.width/2, cy = r.top + r.height/2;
        const base = {bubbles:true, cancelable:true, composed:true,
                      clientX: cx, clientY: cy,
                      screenX: window.screenX + cx, screenY: window.screenY + cy,
                      pageX: window.scrollX + cx, pageY: window.scrollY + cy,
                      button: 0, buttons: 1};
        f.dispatchEvent(new MouseEvent('mousedown', base));
        f.dispatchEvent(new MouseEvent('mouseup', base));
        f.dispatchEvent(new MouseEvent('click', base));
    """)

def game_status(driver):
    """-1 lose, 1 win, 0 ongoing."""
    cls = js_face_class(driver)
    if cls == "facedead": return -1
    if cls == "facewin": return 1
    return 0

def number_of_cell_hidden(board):
    return int(np.sum(board == HIDDEN_CELL))

def pre_opening_move(nrow, ncol):
    return (nrow // 2, ncol // 2)

def update_current_board_local(board, mines):
    if not mines: return board
    for r, c in mines:
        board[int(r), int(c)] = FLAG_CELL
    return board

def open_all_hidden_js(driver, board):
    coords = [(int(r), int(c))
              for r in range(board.shape[0])
              for c in range(board.shape[1])
              if board[r, c] == HIDDEN_CELL]
    js_left_click_cells(driver, coords)

def main():
    game_level = input("SELECT LEVEL (BEGINNER/INTERMEDIATE/EXPERT): ").strip().lower()
    while game_level not in ("beginner", "intermediate", "expert"):
        print("INVALID GAME MODE!")
        game_level = input("SELECT LEVEL (BEGINNER/INTERMEDIATE/EXPERT): ").strip().lower()

    if game_level == "beginner":
        nrow, ncol, num_mines, num_games = 9, 9, 10, 100
    elif game_level == "intermediate":
        nrow, ncol, num_mines, num_games = 16, 16, 40, 50
    else:
        nrow, ncol, num_mines, num_games = 16, 30, 99, 100

    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--incognito")
    options.add_argument("--window-size=1000,900")
    options.page_load_strategy = "eager"

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    minesweeper_url = f"https://minesweeperonline.com/#{game_level}"
    driver.get(minesweeper_url)

    WebDriverWait(driver, 10).until(lambda d: d.execute_script("return !!document.getElementById('1_1');"))

    total_win = 0
    board_solved_proportion = []
    heuristic = Improvement_Heuristic()
    time.sleep(2)
    try:
        for gi in range(1, num_games + 1):
            time.sleep(2)
            print(f"Game {gi} :", end=" ")

            heuristic.reset()
            flag_coords = []

            r0, c0 = pre_opening_move(nrow, ncol)
            js_left_click_cells(driver, [(r0, c0)])

            try:
                WebDriverWait(driver, 5).until(
                    lambda d: d.execute_script(
                        "return !!document.querySelector('.square.open0, .square.open1, .square.open2, .square.open3, .square.open4, .square.open5, .square.open6, .square.open7, .square.open8, .square.bombdeath');"
                    )
                )
            except Exception:
                # If nothing revealed (rare), proceed anyway
                pass

            done = game_status(driver)
            start = time.perf_counter()

            while done == 0:
                t0 = time.perf_counter()
                current_board = js_get_board(driver, nrow, ncol)
                t1 = time.perf_counter()

                # Reflect our local flags so the solver "sees" them
                current_board = update_current_board_local(current_board, flag_coords)

                # If all mines accounted for, open everything else
                if len(flag_coords) >= num_mines:
                    open_all_hidden_js(driver, current_board)

                t2 = time.perf_counter()
                safes, mines = heuristic.solve(current_board)  # must return iterables of (r,c)
                t3 = time.perf_counter()

                if not safes and not mines:
                    # Heuristic stuck: log solved %
                    num_hidden = number_of_cell_hidden(current_board)
                    solved = (nrow * ncol - num_hidden) / (nrow * ncol)
                    print("HEURISTIC STUCK")
                    print(f"Board solved : {solved:.3%}")
                    board_solved_proportion.append(solved)
                    break
                else:
                    if safes:
                        js_left_click_cells(driver, safes)
                        try:
                            WebDriverWait(driver, 3).until(lambda d: d.execute_script("""
                                const coords = arguments[0];
                                for (const [r,c] of coords){
                                    const el = document.getElementById((r+1)+'_'+(c+1));
                                    if (!el) continue;
                                    const cls = el.className || '';
                                    if (cls.includes('open') || cls.includes('bomb')) return true;
                                }
                                return false;
                            """, _norm_coords(safes)))
                        except Exception:
                            pass

                    new_flags = []
                    for r, c in (mines or []):
                        rc = (int(r), int(c))
                        if rc not in flag_coords:
                            flag_coords.append(rc)
                            new_flags.append(rc)
                    # To show flags on the webpage (slightly slower), uncomment:
                    # if new_flags:
                    #     js_rightflag_cells(driver, new_flags)

                done = game_status(driver)
                print(f"[read={t1-t0:.4f}s solve={t3-t2:.4f}s]", end=" ")

            end = time.perf_counter()
            time.sleep(2)
            reset_board(driver)

            if done == 1:
                print("Win")
                total_win += 1
            elif done == -1:
                print("Lose")

            print(f"TIME PLAYED : {end - start:.2f} seconds.")
            try:
                heuristic.get_longest_time_solve()
            except Exception:
                pass
            print()

        print(f"Win rate = {total_win / num_games:.3f}")
        if board_solved_proportion:
            print(f"Mean board solved = {sum(board_solved_proportion)/len(board_solved_proportion):.3f}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
