import os

'''
rules for syntax of given .java files:
- Exceptions are thrown at the beginning of every method if object-like arguments are present
- per method NullPointerExceptions are thrown above IllegalArgumentExceptions
- no sub-classes allowed
'''

class File:
    def __init__(self, path_to_file):
        self.tab = "    " # "\t"
        self.path_to_file = path_to_file
        self.non_objects_keywords = ["int", "double", "float", "String", "long"]
        self.empty_check_keyword = ["String"]


    def add_Exceptions(self):
        with open(self.path_to_file, 'r') as file:
            lines = file.readlines()
        lines.reverse()

        for n, line in enumerate(self.lines):
            content = self.get_method_content(line)

            for var_decl in content:
                tmp = var_decl.split(" ")
                if len(tmp) != 2:
                    continue
                
                decl, var = tmp

                # actual java code manipulation
                if (decl not in self.non_objects_keywords):
                    self.insert_NullPointerException(len(lines)-n, var)
                elif (decl in self.empty_check_keyword):
                    self.insert_IllegalArgumentException(len(lines)-n, var)


    def insert_NullPointerException(self, index, var):
        with open(self.path_to_file, 'r') as file:
            lines = file.readlines()
        
        redo = False
        with open(self.path_to_file, "w") as file:
            for n, line in enumerate(lines):
                if (n != index):
                    file.write(line)
                else:
                    # super() has to be at the beginning of method body which results in shift of exceptions
                    if ("super(" in line):
                        file.write("".join(lines[n:]))
                        keyword = "super("
                        if (var not in line[line.index(keyword)+len(keyword)+1:-3].split(", ")):
                            # all exceptions of objects that aren't cascaded to super constructer have to throw exception
                            redo = True
                        break
                    
                    # if no other object throws a NullPointerException at this point
                    if (" == null" not in line):
                        file.write(2*self.tab + "if (" + var + " == null)\n")
                        file.write(3*self.tab + "throw new NullPointerException();\n")
                        if ('.equals("")' not in line):
                            file.write("\n")
                        file.write(line)
                    # append current object to list of statements to throw NullPointerException
                    else:
                        # exception of current object is already handled
                        if ("(" + var + " == null" in line or " || " + var + " == null" in line):
                            file.write(line)
                            continue
                        
                        keyword = "null"
                        split_index = line.rindex(keyword)+len(keyword)
                        # insert handling to list of statements leading to the NullPointerException
                        file.write(line[:split_index] + " || " + var + " == null" + line[split_index:])
        
        if redo:
            # redo failed insertion with shifting downwards
            self.insert_NullPointerException(index+2, var)
    

    def insert_IllegalArgumentException(self, index, var):
        with open(self.path_to_file, 'r') as file:
            lines = file.readlines()
        
        redo = False
        with open(self.path_to_file, "w") as file:
            for n, line in enumerate(lines):
                if (n != index):
                    file.write(line)
                else:
                    # NullPointerExceptions are handled above IllegalArgumentExceptions
                    if (" == null" in line):
                        if lines[n+2] == "\n":
                            # remove empty line after NullPointerException
                            file.write("".join(lines[n:n+2]+lines[n+3:])) 
                        else:
                            file.write("".join(lines[n:]))
                        redo = True
                        break
                    # super() has to be at the beginning of method body which results in shift of exceptions
                    elif ("super(" in line):
                        file.write("".join(lines[n:]))
                        keyword = "super("
                        if (var not in line[line.index(keyword)+len(keyword):-3].split(", ")):
                            # all exceptions of objects that aren't cascaded to super constructer have to throw exception
                            redo = True
                        break
                    
                    # if no other object throws an IllegalArgumentException at this point
                    if ('.equals("")' not in line):
                        file.write(2*self.tab + "if (" + var + '.equals(""))\n')
                        file.write(3*self.tab + "throw new IllegalArgumentException();\n\n")
                        file.write(line)
                    # append current object to list of statements to throw IllegalArgumentException
                    else:
                        # exception of current object is already handled
                        if ("(" + var + '.equals("")' in line or " || " + var + '.equals("")' in line):
                            file.write(line)
                            continue
                        
                        keyword = '.equals("")'
                        split_index = line.rindex(keyword)+len(keyword)
                        # insert handling to list of statements leading to the IllegalArgumentException
                        file.write(line[:split_index] + " || " + var + '.equals("")' + line[split_index:])
        
        if redo:
            self.insert_IllegalArgumentException(index+2, var)
    

    def is_method(self, str):
        public = "public "
        private = "private "

        if ("(" not in str or ")" not in str or str.index("(") > str.rindex(")")):
            return False
        if (";" in str):
            return False
        
        str = str.replace("\t", "").replace("    ", "")

        if (str[:len(public)] == public or str[:len(private)] == private):
            return True
        else:
            return False
    

    def get_method_content(self, str):
        if not self.is_method(str):
            return ""
        
        content = str[str.index("(")+1:str.index(")")]
        content = content.split(", ")

        return content


def main():
    # os specific path separation
    splitter = "\\"
    current_path = os.path.realpath(__file__)[:os.path.realpath(__file__).rindex(splitter)+1]

    for file in next(os.walk(current_path))[2]:
        keyword = ".java"
        if (file[len(file)-len(keyword):] != keyword):
            continue

        file = File(current_path + splitter + file)
        file.add_Exceptions()


if __name__ == '__main__':
    main()