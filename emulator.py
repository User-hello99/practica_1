from tkinter import *
from tkinter import ttk
import sys
import csv


#GLOBAL VALUES#    
terminal_name = "VFS"
in_name = terminal_name+":~@"
clicked_commands = [""]
vfs_data = {}


#GLOBAL VALUES#


def parse(input_string):
    args = []
    current_arg = ""
    in_quotes = False
    
    for char in input_string:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ' ' and not in_quotes:
            if current_arg:
                args.append(current_arg)
                current_arg = ""
        else:
            current_arg += char
    
    if current_arg:
        args.append(current_arg)
    
    return args

def load_vfs():
    global vfs_data
    try:
        with open("vfs.csv", 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    vfs_data[row[0]] = row[1]
        return f"VFS loaded: {len(vfs_data)} files"
    except:
        return "Error loading VFS"

def st_scripts():
    f = open("scripts/start.sh","r", encoding = "UTF-8").readlines()
    for j in f:
        if "#" in j:
            continue
        else:
            comm = parse(j.split("\n")[0])
            command_name = comm[0]
            command_args = comm[1:]
            yield (command_name,command_args)        
    
#COMMANDS#

def cat(args):
    if not vfs_data:
        return "VFS not loaded"
    if not args:
        return "Specify file"
    if args[0] in vfs_data:
        return vfs_data[args[0]]
    return f"File {args[0]} not found"


def cd(args):
    if len(args) > 1:
        return "Error: Too many arguments"
    
    directory = args[0] if args else "~"
    return f"Go to directory: {directory}"


def ls(args):
    if vfs_data:
        return "\n".join(vfs_data.keys())
    return "No files"

def cexit(args):
    sys.exit()
    
def clear(editor):
    editor.delete("1.0",END)
    editor.insert(END, f"{in_name}")
def echo(args):
    return " ".join(args)

commands = {"cd":cd,"ls":ls,"exit":cexit,"echo":echo,"cat":cat}
#COMMANDS#    



#Ctrl+a(A)
def select_all(event):
    clicked_commands[0] = "ctrl+a"


#Backspace
def on_back(event):
    editor_text = editor.get(1.0, END)
    word_num = editor.index("insert").split('.')
    
    if clicked_commands[0] == "ctrl+a":
        editor.insert("1.0",editor_text)
        
    elif int(word_num[1])<len(in_name)+1:
        return "break"


    clicked_commands[0] = "backspace"

    
#Enter    
def on_enter(event):
   editor_text = editor.get(1.0, END)
   if clicked_commands[0] == "ctrl+a":
        editor.tag_remove(SEL, "1.0", END)
        clicked_commands[0] = "enter"
       
        return "break"
   else:
       cursor_pos = editor.index("insert")
       line_num ,word_num = cursor_pos.split('.')

       command = editor.get(f"{line_num}.{len(in_name)}", f"{line_num}.end").strip()

       
       if command!="":
           args = parse(command)
           command_name = args[0]
           command_args = args[1:]
           if command_name in commands:
               editor.insert(END,'\n'+commands[command_name](command_args))

               editor.insert(END, f"\n{in_name}")
           elif command_name == "clear":
               clear(editor)
           else:
               editor.insert(END,f"\nCommand {command} not definded")

               editor.insert(END, f"\n{in_name}")
           

           line_num ,word_num = editor.index("insert").split('.')

       else:
            editor.insert(END, f"\n{in_name}")

       return "break"
       


def do_command(editor, argv):
    for i in argv[1:]:
        print(i)
        if i == "--script":
            for j in st_scripts():
                editor.insert(END,'\n'+commands[j[0]](j[1]))
                editor.insert(END, f"\n{in_name}")
            
                    
        elif i == "--vfs":
            result = load_vfs()
            editor.insert(END, f"\n{result}")
            editor.insert(END, f"\n{in_name}")
            
        else:
            print("parametrs not definded")

def main():
    global editor
    
    root = Tk()
    root.title(terminal_name)
    root.geometry("700x400")
    root.resizable(False, False)
    root.grid_columnconfigure(0, weight = 1)
    root.grid_rowconfigure(0, weight = 1)
 
    editor = Text(wrap = "none")
    editor.grid(column = 0, row = 0, sticky = NSEW)
     
    ys = ttk.Scrollbar(orient = "vertical", command = editor.yview)
    ys.grid(column = 1, row = 0, sticky = NS)
    editor.insert("1.0", terminal_name+":~@")
   
    editor.bind("<BackSpace>", on_back)
    editor.bind("<Return>", on_enter)
    editor.bind("<Control-a>", select_all)

    editor["yscrollcommand"] = ys.set

    do_command(editor, sys.argv)
    
    root.mainloop()


    
if __name__ == "__main__":
    if len(sys.argv)<2 or len(sys.argv)>3:
        print("Usage: python emulator.py <parametrs>")
        
    main()
        
    
