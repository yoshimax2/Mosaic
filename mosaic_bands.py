import os
import warnings
from PIL import Image

class band:
    r_band = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    g_band = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    b_band = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    def __init__(self):
        self.r_band = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.g_band = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.b_band = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    def get_band(self, band_name):
        if band_name.lower() == "r":
            return self.r_band
        elif band_name.lower() == "g":
            return self.g_band
        elif band_name.lower() == "b":
            return self.b_band

    def set_band(self, band_name, val):
        if band_name.lower() == "r":
            try:
                self.r_band[val//16] = self.r_band[val//16]+1
                return True
            except:
                print("Could not set red band")
        elif band_name.lower() == "g":
            try:
                self.g_band[val//16] = self.g_band[val//16]+1
                return True
            except:
                print("Could not set green band")
        elif band_name.lower() == "b":
            try:
                self.b_band[val//16] = self.b_band[val//16]+1
                return True
            except:
                print("Could not set blue band")
        else:
            print("Not a valid band")
            return False

warnings.filterwarnings('ignore')

images = dict()
loaded_images = []
pixel_data = dict()
red_data = dict()
green_data = dict()
blue_data = dict()
frequencies = dict()
top_three = dict()
averages = dict()
image_list = []
lines = 0
bands = dict()

#Checks path to see if it's a valid pathname
def validate_path(path) -> bool:
    try:
        files = os.scandir(path)
        return True
    except:
        return False

#Loads all images - function no longer used
def load_images(images) -> None:
    for image in images:
        loaded_images.append(image.load())

#Finds frequencies of each RGB value in an image
def find_frequencies(data) -> dict:
    frequency = dict()
    
    for datum in data:
        if type(datum)!= str:
            if datum not in frequency:
                frequency[datum] = 0
            else:
                frequency[datum] += 1
        else:
            frequency["Name"] = datum

    return frequency

#Process RGB values of image and returns them as 2D array containing RGB tuples
def process_target(target) -> list:
    rgb = []
    print("Image is", target.width, "pixels wide and ", target.height, "pixels tall")

    target_data = list(target.getdata())
    
    for x in range(target.height):
        rgb.append([])
        for y in range(target.width):
            rgb[x].append(target_data[(x*target.width)+y])

    return rgb

#Gets length of 2D array
def get_len(twod_array) -> int:
    length = 0
    for x in twod_array:
        for y in x:
            length+=1
    return length

#Updates progress bar
def progress(pos, maxlen) -> None:
    global lines
    if pos == "Start" and maxlen == "Start":
        print("\n0 - - - - 50 - - - - 100")
        return 0

    
    part = maxlen/24
    lines_max = pos//part
    lines_to_draw = lines_max - lines

    while lines_to_draw > 0:
        print("|", end = "")
        lines_to_draw-=1
        lines+=1
    

#Returns average of three RGB values
def average(r, g, b):
    return (r+g+b)/3

#Finds the closest image match for a pixel and returns the image name
def find_match(pixel) -> str:
    
    r = pixel[0]
    g = pixel[1]
    b = pixel[2]
    target_rband = r//16
    target_gband = g//16
    target_bband = b//16
    match = ""
    rmax = 0
    gmax = 0
    bmax = 0

    for image in bands:
        #If there's no match yet, sets first image to match
        if match == "":
            match = image
            rmax = bands[image].get_band("r")[target_rband]
            gmax = bands[image].get_band("g")[target_gband]
            bmax = bands[image].get_band("b")[target_bband]
            avgmax = rmax+gmax+bmax
                
        else:
            try:
                new_rmax = bands[image].get_band("r")[target_rband]
                new_gmax = bands[image].get_band("g")[target_gband]
                new_bmax = bands[image].get_band("b")[target_bband]
                new_avgmax = new_rmax+new_gmax+new_bmax
            except:
                print("", end = "")

            if abs(new_avgmax) > abs(avgmax):
                rmax = new_rmax
                gmax = new_gmax
                bmax = new_bmax
                avgmax = new_avgmax
                match = image
    return match


#Returns top RGB colour found in image
def pick_three(frequency) -> list:
    result = dict()
    top = ["Blank", 0]
    
    for freq in frequency:
        if freq == "Name":
            result["Name"]=frequency[freq]
        else:
            if top[1] < frequency[freq]:
                top[0] = freq
                top[1] = frequency[freq]

    result["Top3"] = top
    return result

def get_averages(data) -> tuple:
    r_count = 0
    g_count = 0
    b_count = 0
    count = 0

    for pixel in data:
        #print(pixel)
        r_count+=pixel[0]
        g_count+=pixel[1]
        b_count+=pixel[2]
        count+=1

    r_avg = r_count/count
    g_avg = g_count/count
    b_avg = b_count/count

    return (r_avg, g_avg, b_avg)

def setup_bands(data, name):
    global bands
    bands[name] = band()
    
    for pixel in data:
        bands[name].set_band("r", pixel[0])
        bands[name].set_band("g", pixel[1])
        bands[name].set_band("b", pixel[2])
        

def combine_data(image) -> list:
    rgb_combined = []

    for i in range(len(red_data[image])):
        rgb_combined.append((red_data[image][i], green_data[image][i], blue_data[image][i]))
    return rgb_combined

def create_mosaic(width, height) -> Image:
    mosaic = Image.new(mode = "RGB", size = (width, height), color = (0,0,0))

    x = 0
    y = 0
    count = 0

    progress("Start", "Start")

    for row in image_list:
        for img in row:
            
            progress(count, get_len(image_list))
            file = Image.open(img)
            small_image = file.resize((30,30))

            mosaic.paste(im = small_image, box = (x,y))
            x+=30
            count+=1
        x = 0
        y+=30

    return mosaic
        
def __main__():

    #Gets valid pathname from user for images
    while True:
        path = input("What's the path of the folder containing your images?: ")

        if validate_path(path):
            break

        else:
            print("Not a valid path. Try again.\n")

    files = os.scandir(path)
    length = len(list(files))
    counter = 0
    halfway = length//2
    three_fourths = (length//4)*3
    one_fourth = length//4
    print("Processing", length, "image files...")

    for file in os.scandir(path):
        if counter == halfway:
            print(counter,"images processed of", length, "... 50% done!")
        elif counter == one_fourth:
            print(counter,"images processed of", length, "... 25% done!")
        elif counter == three_fourths:
            print(counter,"images processed of", length, "... 75% done!")
        counter+=1
        try:
            new_image = Image.open(file.path)
            name = new_image.filename

            """if new_image.width > 100:
                while new_image.width > 100:
                    new_image = new_image.reduce(2)"""

            if new_image.mode != "RGB":
                new_image = new_image.convert(mode = "RGB")
                
            new_image = new_image.resize((100,100))
            images[name] = new_image
        except:
            print("", end="")
    print("Images finished processing.")

    for image in images:
        
        red_data[image] = list(images[image].getdata(0))
        green_data[image] = list(images[image].getdata(1))
        blue_data[image] = list(images[image].getdata(2))
        pixel_data[image] = combine_data(image)

    for data in pixel_data:
        setup_bands(pixel_data[data], data)
    
    while True:
        target_path = input("\nWhat's the name of the image you want to create the mosaic of?: ")

        try:
            target_image = Image.open(path+"/"+target_path)
            print(target_path,"opened successfully")
            break
        except:
            print(path+"/"+target_path,"Not a valid name")

    if target_image.width > target_image.height:
        proportion = target_image.height/target_image.width
        target_image = target_image.resize((100, round(100*proportion)))
    else:
        proportion = target_image.width/target_image.height
        target_image = target_image.resize((round(100*proportion), 100))

    rgb = process_target(target_image)

    for row in range(len(rgb)):
        image_list.append([])
        for pixel in range(len(rgb[row])):
            image_list[row].append(find_match(rgb[row][pixel]))

    mosaic = create_mosaic(target_image.width*30, target_image.height*30)
    
    
    try:
        mosaic.save(path+"/mosaic.png")
        print("\n\nImage successfully saved to",path+"/","as mosaic.png")
    except:
        print("\nUnable to save image")
    

if __name__ == "__main__":
    __main__()

