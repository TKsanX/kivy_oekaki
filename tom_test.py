import tomli_w
import toml
import cv2


with open("./nurie/config.toml") as f:
    data = toml.load(f)

print(data["data"]["tags"])

for tag in data["data"]["tags"]:
    print(tag)
    for img in data["image"][tag]["images"]:
        now_img = cv2.imread("./nurie/" + tag + "/" + img + ".png")
        cv2.imshow("image", now_img)
        cv2.waitKey(0)