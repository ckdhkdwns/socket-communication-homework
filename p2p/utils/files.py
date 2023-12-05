def split_file(input_file, chunk_size= 256000):
    chunks = []
    with open(input_file, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
            
    return chunks


def merge_files(chunks, output_file):
    with open(output_file, 'wb') as output:
        for chunk in chunks:
            output.write(chunk)