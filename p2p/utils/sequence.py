def get_seq_chunk(client_index,  sequence_size, sequence, chunk):
    # 형식 : A0232 + chunk
    header = client_index + ("0" * (sequence_size - len(str(sequence))) + str(sequence))
    return bytes(header, "utf-8") + chunk

def split_received_data(chunk, sequence_size):
    client_index = chr(chunk[0])
    seq = int(chunk[1:sequence_size + 1])
    content = chunk[1 + sequence_size:]
    return client_index, seq, content