# Lossless-Compressor-9000
An attempt at creating a lossless text file compressor in python.

It works on all .txt files and works by creating two files, one for the huffman tree and one for the actual file data itself. 
In testing, it seems to compress the average long text file (around 10 KB) by about 30%, not quite as effective and siginificantly slower than other modern compression algorithms but I think quite decent for a first attempt.

I do cheat a little bit, the tuple storing the huffman tree is stored using CPickle instead of me creating my own tuple storing system but other than that and the use of time.time() to give updates on progress if it is taking a while, the algorithm is completely original (although I expect very similar/the same to many others).
It works by looking at repeated groups of characters (not just repeated words, allowing the compressor to still work effectively even if there are no spaces in the text file) in the text file and then combines those strings with the individual characters used to create a huffman tree and then encodes the text file.

The predominate issue right now is definately performance and optimisation. With large text files and a large word size, RAM usage can easily be in the gigabytes and the time taken for large text files such as the full transcript of the first episode of Star Trek: The Next Generation included in this repository can take over an hour to compress. 
Lowering the maximum word size can help greatly with this however, but it does have an adverse affect on how well it compresses larger files.
