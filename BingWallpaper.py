#!/usr/bin/python3
# -*- coding:utf-8 -*-

from datetime import datetime
import requests,time,os,argparse

class Logger(object):

    @staticmethod
    def error(content,**kwargs):
        time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f]")
        path = "%s/BingWallpaper/.oneclickbingwallpaper.log" % os.path.expanduser('~')

        if "path" in kwargs:
            path = kwargs["path"]

        with open(path,"a+") as file:
            file.write("%s#error :" % time )
            file.write("%s\n" % content )

    @staticmethod
    def info(content,**kwargs):
        time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f]")
        path = "%s/BingWallpaper/.oneclickbingwallpaper.log" % os.path.expanduser('~')
        if "path" in kwargs:
            path = kwargs["path"]

        with open(path,"a+") as file:
            file.write("%s#info :" % time )
            file.write("%s\n" % content )

class Downloader(object):

    @staticmethod
    def get(url,fileName):
        try:
            downloadReponse = requests.get(url)
        except:
            Logger.error("exception throw when getting %s" % fileName )

        if downloadReponse.status_code != 200:
            Logger.error("network error: %s" % str(downloadReponse.status_code) )

        lastIndex = fileName.rfind("/")
        if lastIndex:
            if not os.path.exists(fileName[:lastIndex]):
                os.mkdir(fileName[:lastIndex])
                Logger.info("%s not exist,repairing ..." % fileName[:lastIndex] )

        with open(fileName,"wb") as file:
            file.write(downloadReponse.content)

class BingWallpaper(object):

    def __init__(self,de="",command=""):
        self.baseUrl = "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1"
        self.json = requests.get(self.baseUrl).json()
        imgLocation = self.json['images'][0]['url']
        imgUrl = "https://cn.bing.com%s" % imgLocation
        lastIndex = imgLocation.rfind(".")
        imgSuffix = imgLocation[lastIndex+1:]
        self.imgName = "BingWallpaper-%s.%s" % ( time.strftime("%Y-%m-%d",time.localtime()), imgSuffix )
        self.imgPath = "%s/BingWallpaper/%s" % ( os.path.expanduser('~'), self.imgName)
        self.notifyIconPath = "/usr/share/icons/hicolor/64x64/apps/OneClickBingWallpaper.png"

        self.de = de
        self.command = command

        if not os.path.exists(self.imgPath):
            Downloader.get(imgUrl,self.imgPath)

    def setWallpaper(self):
        Logger.info("setting begin")
        Logger.info("de: %s, command: %s" % (self.de, self.command))

        if self.de == "cinnamon":
            self.command = "gsettings set org.cinnamon.desktop.background picture-uri \"file:///%s\"" % self.imgPath
            Logger.info("cinnamon command status:%s" % str(os.system(self.command)))
        
        elif self.de == "deepin":
            self.command = "gsettings set com.deepin.wrap.gnome.desktop.background picture-uri \"file:///%s\"" % self.imgPath
            Logger.info("deepin command status:%s" % str(os.system(self.command)))
        
        elif self.de == "gnome":
            shell = '''
                gsettings set org.gnome.desktop.background draw-background false && 
                gsettings set org.gnome.desktop.background picture-uri file://# && 
                gsettings set org.gnome.desktop.background draw-background true
            '''
            self.command = shell.replace("#",self.imgPath)
            Logger.info("gnome command status:%s" % str(os.system(self.command)))
        
        elif self.de == "kde":
            plasmashell = '''
                var Desktops = desktops();
                d = Desktops[0];
                d.wallpaperPlugin= "org.kde.image";
                d.currentConfigGroup = Array("Wallpaper","org.kde.image","General");
                d.writeConfig("Image","#");
            '''.replace("#",self.imgPath)
            self.command = "qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript \'#\'".replace("#",plasmashell)
            Logger.info("kde command status:%s" % str(os.system(self.command)))
            # if 'sh: 1: notify-send: not found' in kde , please install libnotify-bin
            # sudo apt install libnotify-bin

        elif self.de == "mate":
            self.command = "gsettings set org.mate.background picture-filename #".replace("#",self.imgPath)
            Logger.info("mate command status:%s" % str(os.system(self.command)))
            
        elif self.de == "wm":
            self.command = "feh --bg-fill %s" % self.imgPath
            Logger.info("feh command status:%s" % str(os.system(self.command)))

        elif self.de == "xfce":
            self.command = "xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image -s %s" % self.imgPath
            Logger.info("xfce command status:%s" % str(os.system(self.command)))

        elif self.command:
            command = self.command.replace("{{}}",self.imgPath)
            Logger.info("%s command status: %s" % ( self.command, str(os.system(command)) ) )

        else:
            Logger.info("not support desktop environment:%s" % str(self.de))
        
        if self.de or self.command:
            self.notify()
        Logger.info("setting finish")

    def notify(self):
        content = self.json['images'][0]['copyright']
        lastIndex = content.rfind("(")
        if os.path.exists(self.notifyIconPath):
            options = "--icon=%s" % self.notifyIconPath
        shell = "notify-send %s:%s %s" % ( time.strftime("%Y-%m-%d",time.localtime()), content[:lastIndex], options)
        print(shell)
        os.system(shell)
    
    def detect(self):
        session = os.getenv("DESKTOP_SESSION")
        keywords = {
            "cinnamon":"cinnamon",
            "deepin":"deepin",
            "gnome":"gnome",
            "mate":"mate",
            "plasma":"kde",
            "xfce":"xfce"
        }
        for key in keywords:
            if key in session:
                self.de = keywords[key]
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto",help="auto detect desktop environment(Beta)",action="store_true")
    parser.add_argument("-d",help="desktop environment: xfce etc")
    parser.add_argument("-c",help="command in your device to set desktop background,{{}} will be replaced with the true images path(not end with \)")
    args = parser.parse_args()

    bw = BingWallpaper(args.d,args.c)
    if args.auto:
        bw.detect()
    bw.setWallpaper()
