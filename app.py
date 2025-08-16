import sys
import tkinter as tk
from tkinter import ttk
import requests
import json
import csv

class Dumper:

    def initial_window(self):
        self.urllabel = tk.Label(root, text="URL: ")
        self.urllabel.config()
        self.urlentry = tk.Entry(root)
        self.urlentry.pack(pady=5)

        self.keylabel = tk.Label(root, text="Key: ")
        self.keylabel.config()
        self.keyentry = tk.Entry(root)
        self.keyentry.pack(pady=5)

        self.button_next = tk.Button(root, text="Fetch Objects", command=self.on_click_next)
        self.button_next.pack(pady=5)
        self.button_quit = tk.Button(root, text="Exit", command=self.quit)
        self.button_quit.pack(pady=5)        

    def on_click_next(self):
        self.url = self.urlentry.get()
        self.key = self.keyentry.get()
        

        headers = {
            "Authorization": f"Bearer {self.key}"
        }
        try:
            
            response = requests.get(self.url, headers=headers)
            
            self.data = json.loads(response.content)
        except:
            self.quit()
       

        self.display_objects()

    def quit(self):
        self.root.destroy()
        newroot = tk.Tk()
        newroot.title("Error")
        print("Could not fetch from API.")
        self.var_detail = tk.StringVar(value="API Fetch failed.")
        self.lbl_detail = ttk.Label(newroot, textvariable=self.var_detail, padding=10, wraplength=600, justify="left")
        self.lbl_detail.pack(fill="x")
        self.exit_button = tk.Button(newroot, text="Exit", command=lambda : quit())
        self.exit_button.pack(pady=10)
        newroot.mainloop()
        
    def display_objects(self):
        self.root.destroy()
        self.root = tk.Tk()
        frm_list = ttk.Frame(self.root, padding=10)
        frm_list.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(frm_list, height=12, activestyle="dotbox")
        self.listbox.pack(side="left", fill="both", expand=True)
        for item in self.data:
            self.listbox.insert(tk.END, item["label"])
            
        self.next_btn = tk.Button(self.root, text="Next", command=self.go_next)
        self.next_btn.pack(pady=5)
        frm_list.pack(fill="both", expand=True)

    def go_next(self):
        fulldata = []
        selection = self.listbox.curselection()
        shortlabel = self.data[selection[0]]['shortLabel']
        fetchurl = f"{self.url}data/{shortlabel}"
        try:
            headers = {
            "Authorization": f"Bearer {self.key}"
        }
            response = requests.get(fetchurl, headers=headers)
            data = json.loads(response.content)

            fulldata.extend(data["data"])
            fetchurl = data["nextUrl"]

            while fetchurl:
                data = json.loads(response.content)
                fulldata.extend(json.loads(response.content))
                fetchurl = data["nextUrl"]
                print(f"{fetchurl} - {response.status_code}")
                if (not fetchurl):
                    break
                else:
                    response = requests.get(fetchurl, headers=headers)

            self.json_to_csv_out(shortlabel, fulldata)
        except:
            print(f"failed {response.status_code}")

            self.quit()

    def json_to_csv_out(self, shortlabel, data):
        fieldnames = data[0].keys()
        with open(f"{shortlabel}.csv", "w") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

    def __init__(self, root):
        self.root = root
        self.url = ""
        self.key = ""
        self.data = {}
        self.initial_window()

        frm_top = ttk.Frame(root, padding=10)
        frm_top.pack(fill="x")

 
    def parse_objects(self, objects):
        modules = []
        dimensions = []
        for obj in objects:
            newObj ={"label": obj["label"], "shortLabel": obj["shortLabel"]}
            if obj["objectType"] == "Module":
                modules.append(newObj)
            else:
                dimensions.append(newObj)
            
if __name__ == '__main__':
    root = tk.Tk()
    dumper = Dumper(root)
    root.mainloop()

