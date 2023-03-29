
# import os

# # define the mapping of numbers to new names
# name_map = {
#     "01": "28MaSlow",
#     "02": "28MaSlow-LessBlinking",
#     "03": "RestingGray",
#     "04": "RestingVROff",
#     "05": "RestingClosedEyes",
#     "06": "28MaFast",
#     "07": "Explorepy-TL",
#     "08": "Explorepy-TR",
#     "09": "Explorepy-BL",
#     "10": "Explorepy-BR",
#     "11": "23Ma-BL",
#     "12": "23Ma-ML",
#     "13": "23Ma-TL",
#     "14": "23Ma-TR"
# }

# # get a list of all files in the current directory
# files = os.listdir()

# # loop over the files and rename them
# for file in files:
#     if file.endswith(".dap") or file.endswith(".dat") or file.endswith(".rs3"):
#         if file == "test.dat":
#             continue
#         # extract the number from the filename
#         number = file.split("_")[3].split(".")[0]
#         # get the new name based on the number
#         new_name = name_map.get(number) + file[-4:]
#         # rename the file
#         os.rename(file, new_name)
