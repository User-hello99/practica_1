from tkinter import *
from tkinter import ttk
import sys
import csv


#GLOBAL VALUES#    
terminal_name = "VFS"
in_name = terminal_name+":~@"
in_name_before = in_name
clicked_commands = [""]
vfs_data = {}
file_owners = {}
current_path = "/"
users = []

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

def load_vfs(argv):
    global vfs_data
    try:
        vfs_data = {}
        with open(argv, 'r') as f:
            reader = csv.reader(f)
            
            for row in reader:
                if len(row) == 4:  
                    path = row[0]
                    filename = row[1]
                    content = row[2]
                    user = row[3]
                    full_path = path.rstrip('/') + '/' + filename
                    vfs_data[full_path] = [content,user]
        return f"VFS loaded: {len(vfs_data)} files"
    except Exception as e:
        return f"Error loading VFS: {str(e)}"

def st_scripts(argv):
    f = open(argv,"r", encoding = "UTF-8").readlines()
    for j in f:
        if "#" in j:
            continue
        else:
            comm = parse(j.split("\n")[0])
            command_name = comm[0]
            command_args = comm[1:]
            yield (j,command_name,command_args)        
    
#COMMANDS#

def cd(args):
    global current_path, in_name
    if len(args) > 1:
        return "Error: Too many arguments"
    
    if not args:
        current_path = "/"
        in_name = f"{terminal_name}:~@"
        return ""
    
    new_path = args[0]
    if new_path == "..":
        if current_path != "/":
            parts = current_path.rstrip('/').split('/')
            current_path = '/'.join(parts[:-1]) or "/"
            in_name = f"{terminal_name}:~{current_path}@" if current_path != "/" else f"{terminal_name}:~@"
        return ""
    else:

        target_path = current_path.rstrip('/') + '/' + new_path
        dir_exists = any(path.startswith(target_path + '/') for path in vfs_data.keys())
        
        if dir_exists or new_path == "home":  # временно для теста
            current_path = target_path
            in_name = f"{terminal_name}:~{current_path}@" if current_path != "/" else f"{terminal_name}:~@"
            return f"Go to directory: {current_path}"
        else:
            return f"Error: Directory '{new_path}' not found"

def ls(args):
    if not vfs_data:
        return "No files"
    
    target_path = current_path
    if len(args) == 1:
        target_path = args[0] if args[0].startswith("/") else current_path.rstrip('/') + '/' + args[0]
    if len(args)==2 and args[0] == "-l":
        target_path = args[1] if args[1].startswith("/") else current_path.rstrip('/') + '/' + args[1]
        return vfs_data[target_path][1]
    files = []
    for full_path in vfs_data.keys():
        dir_path = '/'.join(full_path.split('/')[:-1]) or "/"
        filename = full_path.split('/')[-1]
        
        if dir_path == target_path:
            files.append(filename)
        else:
            if dir_path not in files and dir_path!= "/":
                files.append(dir_path)
    
    if files:
        return "\n".join(files)
    return "Directory is empty"


def cat(args):
    if not vfs_data:
        return "VFS not loaded"
    if not args:
        return "Specify file"
    
    filename = args[0]
    full_path = current_path.rstrip('/') + '/' + filename
    
    if full_path in vfs_data:
        return vfs_data[full_path][0]
    
    return f"File {filename} not found"


def cexit(args):
    sys.exit()
    
def clear(editor):
    editor.delete("1.0",END)
    editor.insert(END, f"{in_name}")

def echo(args):
    return " ".join(args)

def pwd(args):
    return current_path

def du(args):
    if not vfs_data:
        return "VFS not loaded"
    
    total_size = 0
    for content in vfs_data.values():
        total_size += len(str(content[0]))
    
    return f"Total size: {total_size} bytes"


def chown(args):
    if len(args) < 2:
        return "Error: chown <OWNER> <FILE>"
    
    owner, filename = args[0], args[1]
    full_path = current_path.rstrip('/') + '/' + filename
    
    if full_path not in vfs_data:
        return f"File '{filename}' not found"
    
    vfs_data[full_path][1] = owner
    return f"Owner changed to '{owner}'"

def touch(args):
    if not args:
        return "Error: touch FILENAME"
    
    filename = args[0]
    full_path = current_path.rstrip('/') + '/' + filename

    if full_path in vfs_data:
        return f"File '{filename}' exists"
    
    vfs_data[full_path] = ""
    file_owners[full_path] = "root"

    return f"File '{filename}' created"


commands = {"cd":cd,
            "ls":ls,
            "exit":cexit,
            "echo":echo,
            "cat":cat,
            "pwd":pwd,
            "du":du,
            "chown":chown,
            "touch":touch}

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
    print("Arguments:", argv)
    
   
    i = 1
    while i < len(argv):
        print(f"Processing argument {i}: {argv[i]}")
        
        if argv[i] == "--script":
            if i + 1 < len(argv) and argv[i + 1] != "--vfs":
                script_file = argv[i + 1]
                print(f"Loading script: {script_file}")
                
                try:
                    for j in st_scripts(script_file):
                        editor.insert(END, j[0])
                        editor.insert(END, "\n" + commands[j[1]](j[2]))
                        editor.insert(END, f"\n{in_name}")
                        editor.see(END)  # Прокрутка к концу
                        editor.update()   # Обновление интерфейса
                except Exception as e:
                    editor.insert(END, f"\nError loading script: {str(e)}")
                    editor.insert(END, f"\n{in_name}")
                
                i += 2  
                
            else:
                editor.insert(END, "\nError: --script requires a filename")
                editor.insert(END, f"\n{in_name}")
                return
                
        elif argv[i] == "--vfs":
            if i + 1 < len(argv) and argv[i + 1] != "--script":
                vfs_file = argv[i + 1]
                print(f"Loading VFS: {vfs_file}")
                
                try:
                    result = load_vfs(vfs_file)
                    editor.insert(END, f"\n{result}")
                    editor.insert(END, f"\n{in_name}")
                except Exception as e:
                    editor.insert(END, f"\nError loading VFS: {str(e)}")
                    editor.insert(END, f"\n{in_name}")
                
                i += 2  
                
            else:
                editor.insert(END, "\nError: --vfs requires a filename")
                editor.insert(END, f"\n{in_name}")
                return
                
        else:
            # Неизвестный аргумент
            editor.insert(END, f"\nUnknown argument: {argv[i]}")
            editor.insert(END, f"\n{in_name}")
            i += 1


       
                
        

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
    editor.insert("1.0", in_name)
   
    editor.bind("<BackSpace>", on_back)
    editor.bind("<Return>", on_enter)
    editor.bind("<Control-a>", select_all)

    editor["yscrollcommand"] = ys.set

    do_command(editor, sys.argv)
    
    root.mainloop()


    
if __name__ == "__main__":
    if len(sys.argv)<2 or len(sys.argv)>3:
        print("Usage: python emulator.py <parametrs>")

        sys.exit(1)
    main()
        
    
