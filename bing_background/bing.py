import os
import sys
import requests 
import datetime

class Bing():
    """Outer Class"""

    def __init__(self, idx=0):

        self.day = idx
        self.number_of_images = 1
        # instantiating the ImageFile class (Inner class)
        self.image = self.Image()
        
    def __request_api(self):
        try:
            # idx parameter determines where to start from: 0 is default as the current day
            response = requests.get("https://www.bing.com/HPImageArchive.aspx?format=js&" \
                "idx=%s&n=%s&mkt=en-US" % (str(self.day), str(self.number_of_images)))

        except HTTPError as http_err:
            print('HTTP error occurred: {}'.format(http_err))

        except Exception as err:
            print('Other error occurred: {}'.format(err))
        else:
            # Get json
            json_data = response.json()
            return json_data


    def get_image_url(self, is_a_background=True):
        """
        Method to get the full url of a Bing’s background for a given day(idx)
        """
        json_data = self.__request_api()
        n = self.number_of_images
        # Form the URL for the image
        image_data = json_data['images']
        
        info_list = []
        for i in range(self.number_of_images):
            image_url = image_data[i]["url"].split("&")[0]
            full_url = "https://www.bing.com" + image_url

            detail_dict = {
                "url" : full_url,
                "title" : image_data[i]["title"],
                "copyright" : image_data[i]["copyright"]
            }
            info_list.append(detail_dict)

        # Check the number of fetched urls
        if len(info_list) > 1: return info_list

        if is_a_background:   
            
            self.__download_image(full_url)

        else:   #if __name__ != "__main__":
            return full_url

    def get_list_of_urls(self, start=0, end=7):

        assert start <= end, "first number <= last number is allowed"
        self.number_of_images = (end - start)+1
        self.day= start
        
        return self.get_image_url(0)

    def __download_image(self, url):

        # download the image
        image_file = requests.get(url)
        self.__set_file_path(image_file)

    def __set_file_path(self, image_file):

        day = self.day
        image_name = self.image.get_image_name(day)
        full_path = self.image.save_file(image_file, image_name)   
        self.__set_linux_background(full_path)

    def __set_linux_background(self, save_path):
        
        # command to set background
        os.system("gsettings set org.gnome.desktop.background picture-uri file://"+save_path)
        return print("Done!")

    class Image():
        """Inner class"""

        def __init__(self):
            pass

        def get_image_name(self, day):
            """
            Method to set date of image as its name in this format: Y-m-d.jpg
            """
            image_name = ''
            
            today = datetime.date.today()

            if day == 0:
                image_name = str(today) + ".jpg"
            else:
                pre_date_str = today - datetime.timedelta(days=day)
                image_name = str(datetime.datetime.strftime(pre_date_str, "%Y-%m-%d")) + ".jpg"
                
            return image_name

        def save_file(self, image_file , file_name):
            
            path = self.__get_path_to_save()
            with open(path + file_name, 'wb') as f:
                f.write(image_file.content)
            print("saved successfully!")

            return path+file_name

        def __get_path_to_save(self):

            # get HOME path
            home_path = os.path.expanduser("~")

            # save_dir is used to set the location where Bing pics of the day are stored.
            save_dir = home_path + "/Pictures/.bing-images/"

            # create directory if it does not already exist
            os.makedirs(save_dir, exist_ok=True)

            return save_dir


def check_run_from_cmd():

    # if(len(sys.argv)==0):
    if not sys.stdout.isatty():
        
        raise Exception("Please run the script from the Command Line")
    else:
        print("You're running in a real terminal")
        
    return True

def main():
    # if any argument is not received from the user,the defaul is current day =0 
    user_day = 0

    if check_run_from_cmd():  
        # if user passed an optional argument
        if len(sys.argv)>1:
            # the first element is the name of program: sys.arg[0]==bing.py
            user_day = int(sys.argv[1])
            # if not condition, raise an error
            assert 0< user_day <=7, "Only numbers between 1 and 7 as previous days are allowed!"
            
        Bing(user_day).get_image_url()


if __name__ == "__main__":
    main()   