#This is the main file to execute all the sub files
import subprocess

#Retrieve the news from the cryptopanic API
subprocess.run(["python", "cryptopanic_News_Request.py"])

