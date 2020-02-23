from time import time
from _pickle import dump, load
NUMBER_BASE=2 #For now, do not change
END_STRING="END" #String to represent the end of the file. Can be any string but has to be the same when compressing and decompressing.
CHUNK_SIZE=8 #For now, do not change
WORD_SIZE_LIMIT=100 #Increase for better compression and a cost to performance

def read_file():
    print("Enter file name (make sure file is a text file and is in the same directory)")
    file_name=input()
    try:
        if file_name[-4:]==".txt":
            file_handle=open(file_name,"r")
        else:
            file_handle=open(file_name+".txt","r")
        file_data=file_handle.read()
        file_handle.close()
    except FileNotFoundError:
        print("File not found, please try again.")
        file_data=read_file()
    return file_data

def read_compressed():
    print("Enter file name (do not enter a file extension and make sure both .data and .meta files are present and in the same directory)")
    file_name=input()
    try:
        file_handle1=open(file_name+".meta","rb")
        meta_data=load(file_handle1)
        file_handle1.close()
        file_handle2=open(file_name+".data","rb")
        file_data=file_handle2.read()
        file_handle2.close()
        converted_file_data=""
        for chunk in file_data:
            converted_file_data=converted_file_data+format(chunk,'08b')
    except FileNotFoundError:
        print("File not found, please try again.")
        meta_data,file_data=read_compressed()
    return meta_data, converted_file_data
        
def write_file(metadata,filedata):
    print("Enter file name to save as")
    file_name=input()
    file_handle1=open(file_name+".meta","wb")
    dump(metadata, file_handle1)
    file_handle1.close()
    file_handle2=open(file_name+".data","wb")
    binary_array=[]
    if not len(filedata)%CHUNK_SIZE==0:
        for _ in range(0,CHUNK_SIZE-len(filedata)%CHUNK_SIZE):
            filedata=filedata+"0"
    for i in range(0,len(filedata),CHUNK_SIZE):
        binary_array.append(int(filedata[i:i+CHUNK_SIZE],2))
    file_handle2.write(bytearray(binary_array))
    file_handle2.close()

def write_text(data):
    print("Do you want to display the uncompressed plaintext in this window or save to a file? (Enter 1 or 2)")
    user_input=input()
    if user_input=="1":
        print(data)
    elif user_input=="2":
        print("Enter file name to save as")
        file_name=input()
        file_handle=open(file_name+".txt","w")
        file_handle.write(data)
        file_handle.close()
    else:
        print("Invalid input, please try again")
        write_text(data)
    
def build_dictionary(file_data):
    debug=time()
    dictionary={}
    for min_index in range(0,len(file_data)-1):
        for max_index in range(min_index+2,len(file_data)+1):
            if not (max_index-min_index)>len(file_data)/2 and not (max_index-min_index)>WORD_SIZE_LIMIT and not file_data[min_index:max_index]==END_STRING:
                if not file_data[min_index:max_index] in dictionary.keys():
                    dictionary[file_data[min_index:max_index]]=[1,[[min_index,max_index]],False]
                else:
                    dictionary[file_data[min_index:max_index]][0]+=1
                    dictionary[file_data[min_index:max_index]][1].append([min_index,max_index])
            if debug+5<time():
                debug=time()
                print("This seems to be taking a while; "+str(min_index/(len(file_data)-1)*100)+"% complete")
    print("Dictionary construction phase 1 complete")
    removing_conflicts=False
    for key in list(dictionary.keys()):
        if dictionary[key][0]<2:
            del dictionary[key]
    removing_conflicts=True
    while removing_conflicts:
        removing_conflicts=False
        for key in list(dictionary.keys()):
            if key in dictionary.keys():
                for key2 in list(dictionary.keys()):
                    if not key2==key:
                        for letter in key: #Save performance by not checking strings with no letters in common
                            if letter in key2:
                                key1_ranges=dictionary[key][1]
                                key2_ranges=dictionary[key2][1]
                                for key1_range in key1_ranges:
                                    for key2_range in key2_ranges:
                                        if key1_range[0]<=key2_range[0]<=key1_range[1] or key1_range[0]<=key2_range[1]<=key1_range[1]:
                                            if (len(key)-1)*(dictionary[key][0]-1) > (len(key2)-1)*(dictionary[key2][0]-1):
                                                dictionary[key2][1].remove(key2_range)
                                                dictionary[key2][0]-=1
                                                removing_conflicts=True
                                                if dictionary[key2][0]<2:
                                                    del dictionary[key2]
                                                    break
                                    if key2 not in dictionary.keys():
                                        break
                                    if debug+5<time():
                                            debug=time()
                                            print("This seems to be taking a while; "+str(len(dictionary))+" items need checking")
                                break
    print("Dictionary construction phase 2 complete")
    return dictionary
    
def dictionary_compress(file_data,dictionary):
    debug=time()
    compressed_data=[]
    letter_num=0
    compressing=True
    new_dictionary={}
    for key in dictionary.keys():
        new_dictionary[key]=dictionary[key][0]
    while not letter_num==len(file_data):
        temp_word=""
        options=list(dictionary.keys())
        while len(options)>0:
            temp_word=temp_word+file_data[letter_num]
            letter_num+=1
            to_remove=[]
            for option_num in range(0,len(options)):
                if not temp_word==options[option_num][0:len(temp_word)]:
                    to_remove.append(options[option_num])
                elif len(temp_word)==1:
                    for option_range in dictionary[options[option_num]][1]:
                        if option_range[0]==letter_num-1:
                            break
                    else:
                        to_remove.append(options[option_num])
            for each in to_remove:
                options.remove(each)
            if letter_num==len(file_data):
                temp_word=temp_word+"a"
                letter_num+=1
                break
        if temp_word[0:len(temp_word)-1] in list(dictionary.keys()):
            compressed_data.append(temp_word[0:len(temp_word)-1])
            letter_num-=1
        else:
            compressed_data.append(temp_word[0])
            if temp_word[0] in new_dictionary.keys():
                new_dictionary[temp_word[0]]+=1
            else:
                new_dictionary[temp_word[0]]=1
            letter_num-=len(temp_word)-1
        if debug+5<time():
                        debug=time()
                        print("This seems to be taking a while; "+str(letter_num/len(file_data)*100)+"% complete (final stage now!)")
        new_dictionary[END_STRING]=1
    return compressed_data,new_dictionary

def create_huffman(file_data,dictionary):
    maximum=0
    while len(dictionary)>1:
        for key in dictionary.keys():
            maximum=max(dictionary[key],maximum+1)
        minimums=[]
        for _ in range(0,NUMBER_BASE):
            minimums.append([maximum,""])
        for key in list(dictionary.keys()):
            for index in range(0,NUMBER_BASE):
                if dictionary[key]<minimums[index][0]:
                    minimums[index][1]=key
                    minimums[index][0]=dictionary[key]
                    break
        for index in range(0,NUMBER_BASE):
            if not minimums[index][1]=='':
                del dictionary[minimums[index][1]]
        next_dictionary=dictionary.copy()
        new_key=[]
        new_value=0
        for index in range(0,NUMBER_BASE):
            new_key.append(minimums[index][1])
            new_value+=minimums[index][0]
        next_dictionary[tuple(new_key)]=new_value
        dictionary=next_dictionary
    dictionary=list(dictionary.keys())[0]
    return dictionary

def recursive_lookup_create(group,lookup,code,mode):
    if type(group)==tuple:
        for digit in range(0,len(group)):
            lookup.update(recursive_lookup_create(group[digit],{},code+str(digit),mode))
        return lookup
    else:
        if mode=="w":
            return {group:code}
        else:
            return {code:group}
        

def huffman_encode(file_data,dictionary):
    lookup_dict=recursive_lookup_create(dictionary,{},"","w")
    compressed_file=""
    for each in file_data:
        compressed_file+=lookup_dict[each]
    compressed_file+=lookup_dict[END_STRING]
    return compressed_file

def huffman_decode(meta_data,file_data):
    lookup_dict=recursive_lookup_create(meta_data,{},"","r")
    code=""
    decompressed=""
    for bit in file_data:
        code=code+bit
        if code in lookup_dict.keys():
            if lookup_dict[code]==END_STRING:
                break
            else:
                decompressed=decompressed+lookup_dict[code]
                code=""
    return decompressed
            
def main():
    print("Compress or decompress? (Enter 1 or 2)")
    user_input=input()
    if user_input=="1":
        file_data=read_file()
        dictionary=build_dictionary(file_data)
        compressed_data,dictionary=dictionary_compress(file_data,dictionary)
        dictionary=create_huffman(compressed_data,dictionary)
        file_data=huffman_encode(compressed_data,dictionary)
        write_file(dictionary,file_data)
    elif user_input=="2":
        meta_data,file_data=read_compressed()
        text=huffman_decode(meta_data,file_data)
        write_text(text)
    else:
        print("Invalid input")
        main()
main()
