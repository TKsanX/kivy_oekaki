import PySimpleGUI as sg
from PIL import Image
import random
import io

def load_image(filename, size=(500, 500)):
    img = Image.open(filename)
    img = img.resize(size)
    return img

def split_image(img, grid_size):
    width, height = img.size
    tile_width, tile_height = width // grid_size, height // grid_size
    tiles = []
    for y in range(0, height, tile_height):
        for x in range(0, width, tile_width):
            box = (x, y, x + tile_width, y + tile_height)
            tile = img.crop(box)
            tiles.append(tile)
    return tiles

def get_image_data(img):
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

def create_window(grid_size):
    layout = [
        [sg.Text("Image Puzzle", font=("Helvetica", 20))],
        [sg.Button("Load Image")],
        [sg.Frame("Puzzle", [[sg.Button("", size=(3, 1), key=(i, j)) for j in range(grid_size)] for i in range(grid_size)])],
        [sg.Button("Shuffle"), sg.Button("Solve")]
    ]
    return sg.Window("Image Puzzle", layout, finalize=True)

def main():
    grid_size = 5  # グリッドサイズを5に変更
    window = create_window(grid_size)
    tiles = []
    solved_state = []

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == "Load Image":
            filename = sg.popup_get_file("Choose an image file")
            if filename:
                img = load_image(filename)
                tiles = split_image(img, grid_size)
                solved_state = tiles.copy()
                random.shuffle(tiles)
                for i in range(grid_size):
                    for j in range(grid_size):
                        window[(i, j)].update(image_data=get_image_data(tiles[i*grid_size + j]))

        if event == "Shuffle":
            random.shuffle(tiles)
            for i in range(grid_size):
                for j in range(grid_size):
                    window[(i, j)].update(image_data=get_image_data(tiles[i*grid_size + j]))

        if event == "Solve":
            tiles = solved_state.copy()
            for i in range(grid_size):
                for j in range(grid_size):
                    window[(i, j)].update(image_data=get_image_data(tiles[i*grid_size + j]))

        if isinstance(event, tuple):
            i, j = event
            if 0 <= i < grid_size and 0 <= j < grid_size:
                idx = i * grid_size + j
                if idx + 1 < len(tiles):
                    tiles[idx], tiles[idx + 1] = tiles[idx + 1], tiles[idx]
                    window[event].update(image_data=get_image_data(tiles[idx]))
                    window[(i, j + 1) if j + 1 < grid_size else (i + 1, 0)].update(image_data=get_image_data(tiles[idx + 1]))

    window.close()

if __name__ == "__main__":
    main()