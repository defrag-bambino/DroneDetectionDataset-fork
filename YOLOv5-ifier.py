import argparse
import os
import tqdm


def yolov5ify(imgs_path, include_negatives):
    # trim away everything after the last '/' to get the dataset root dir
    path = imgs_path.split("/")[:-1]
    path = "/".join(path) + "/"

    # create the labels_path by appending '_XMLs'
    labels_path = imgs_path + "_XMLs"

    # create the 'images' and 'labels' dirs, if they dont exist already
    os.makedirs(path + "images", exist_ok=True)
    os.makedirs(path + "labels", exist_ok=True)

    # init counters
    neg_counter = 0
    pos_counter = 0
    corrupted_counter = 0

    input_imgs = len(os.listdir(imgs_path))
    input_lbls = len(os.listdir(labels_path))

    # for all the files in the images folder, check if they are images
    for file in tqdm.tqdm(os.listdir(imgs_path)):
        if file.endswith(".jpg") or file.endswith(".png"):
            # find the corresponding label file
            label_file = file.split(".")[0] + ".xml"

            # if the label file does not exist or include_negatives is set to false, skip this image/label pair
            if (
                not os.path.exists(labels_path + "/" + label_file)
                and not include_negatives
            ):
                continue
            elif (
                not os.path.exists(labels_path + "/" + label_file) and include_negatives
            ):
                # copy the image to the images dir
                os.system("cp " + imgs_path + "/" + file + " " + path + "images/")
                # create an empty label txt file in the 'labels' folder
                os.system("touch " + path + "labels/" + file.split(".")[0] + ".txt")
                neg_counter += 1
                continue

            # parse the .xml file and get the bounding box info along with the width and height of the image
            with open(labels_path + "/" + label_file, "r") as f:
                width = -1
                height = -1
                xmin = -1
                ymin = -1
                xmax = -1
                ymax = -1
                class_name = -1
                lines = f.readlines()
                for line in lines:
                    if line.__contains__("<width>"):
                        width = int(line.split("<width>")[1].split("</width>")[0])
                    elif line.__contains__("<height>"):
                        height = int(line.split("<height>")[1].split("</height>")[0])
                    elif line.__contains__("<xmin>"):
                        xmin = int(line.split("<xmin>")[1].split("</xmin>")[0])
                    elif line.__contains__("<ymin>"):
                        ymin = int(line.split("<ymin>")[1].split("</ymin>")[0])
                    elif line.__contains__("<xmax>"):
                        xmax = int(line.split("<xmax>")[1].split("</xmax>")[0])
                    elif line.__contains__("<ymax>"):
                        ymax = int(line.split("<ymax>")[1].split("</ymax>")[0])
                    elif line.__contains__("<name>"):
                        class_name = line.split("<name>")[1].split("</name>")[0]
                if (
                    width == -1
                    or height == -1
                    or xmin == -1
                    or ymin == -1
                    or xmax == -1
                    or ymax == -1
                    or class_name == -1
                ):
                    print("Error: Could not parse label file " + label_file)
                    corrupted_counter += 1
                    continue
                # use the obtained x,y coordinates to compute the x_center and y_center and width and height of the object, and normalize them
                x_center = ((xmin + xmax) / 2) / width
                y_center = ((ymin + ymax) / 2) / height
                width = (xmax - xmin) / width
                height = (ymax - ymin) / height

                # create the new label txt file in the 'labels' folder and write the bounding box info to it in the format: 0, x_center, y_center, width, height
                with open(path + "labels/" + file.split(".")[0] + ".txt", "w") as labl:
                    labl.write(
                        str(0)
                        + " "
                        + str(x_center)
                        + " "
                        + str(y_center)
                        + " "
                        + str(width)
                        + " "
                        + str(height)
                    )

            # copy the image file to the 'images' dir
            os.system("cp " + imgs_path + "/" + file + " " + path + "images/")
            pos_counter += 1

    # print statistics
    print(
        "\nCreated "
        + str(pos_counter)
        + " positive labels and "
        + str(neg_counter)
        + " negative labels out of "
        + str(input_imgs)
        + " images and "
        + str(input_lbls)
        + " labels."
    )
    print("Corrupted labels: " + str(corrupted_counter))


if __name__ == "__main__":
    # parse the args using argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--imgs_path", type=str, help="Path to the images folder")
    args = parser.parse_args()

    # ask the user if they would like to include negative labels
    include_negatives = input(
        "Would you like to include negative image/label pairs (ones not containing drones)? (y/n): "
    )
    if include_negatives == "y":
        include_negatives = True
    else:
        include_negatives = False

    yolov5ify(os.path.normpath(args.imgs_path), include_negatives)
