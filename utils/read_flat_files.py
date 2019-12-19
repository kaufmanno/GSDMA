import pandas as pd
import numpy as np

def read_electrode_string_geometry(filename, file_path='../electrode_strings/'):
    """
    Reads an electrode string file

    :param filename: electrode string's filename
    :param file_path: path to electrode string file
    :return:
    """
    electrode_string = {}
    eof = False
    with open(file_path + filename, 'rb') as csv_file:
        line = csv_file.readline()
        while not eof:
            if not (line == b'# electrode string name\n'):
                print('invalid file format: ' + line.decode('utf-8'))
                return
            es_name = csv_file.readline().decode('utf-8')[:-1]
            line = csv_file.readline()
            if not (line == b'# electrode string origin coordinates\n'):
                print('invalid file format: ' + line.decode('utf-8'))
                return
            line = csv_file.readline()
            origin_coords = [float(i) for i in line.decode('utf-8').split()]
            line = csv_file.readline()
            if not (line == b'# electrodes relative coordinates\n'):
                print('invalid file format: ' + line.decode('utf-8'))
                return
            end_of_electrode_string = False
            electrodes_coordinates = []
            while not end_of_electrode_string:
                line = csv_file.readline()
                if line == b'' or line == b'\n':
                    end_of_electrode_string = True
                    eof = True
                elif line == b'# electrode string name\n':
                    end_of_electrode_string = True
                    print('Warning : only one electrode string per file ! Reading only the first one...')
                    eof = True
                else:
                    electrodes_coordinates.append([float(i) for i in line.decode('utf-8').split()])
            electrode_string[es_name] = [origin_coords, {int(i[0]): (i[1], i[2], i[3]) for i in electrodes_coordinates}]
    return es_name, electrode_string

def read_boreholes_description(filename):
    boreholes = {}
    eof = False
    with open(filename, 'rb') as csv_file:
        line = csv_file.readline()
        while not eof:
            if (line == b'# borehole name\n') or (line == b'# borehole name\t\t\t\t\n') \
                    or (line == b'\xEF\xBB\xBF# borehole name\n') \
                    or (line == b'\xEF\xBB\xBF# borehole name\t\t\t\t\n'):
                tl = -1 # linux line terminator format \n
            else:
                if (line == b'# borehole name\r\n') or (line == b'# borehole name\t\t\t\t\r\n') \
                        or (line == b'\xEF\xBB\xBF# borehole name\r\n') \
                        or (line == b'\xEF\xBB\xBF# borehole name\t\t\t\t\r\n'):
                    tl = -2  # windows line terminator format \r\n
                    print(filename + ': Warning windows format: please copy/paste file content in gedit!')
                else:
                    print('invalid file format: ' + line.decode('utf-8') + ' | ' + line.decode('hex'))
                    return
            bh_name = csv_file.readline().decode('utf-8')[:tl].split('\t')[0]
            boreholes[bh_name] = {}
            line = csv_file.readline()
            if not ((line == b'# borehole description\n') or (line == b'# borehole description\t\t\t\t\n') or
                        (line == b'# borehole description\r\n') or (line == b'# borehole description\t\t\t\t\r\n')):
                print('invalid file format: ' + line.decode('utf-8'))
                return
            else:
                line = csv_file.readline()
            end_of_borehole = False
            former_line_descr = [None, None, None, None, None]
            while not end_of_borehole:
                line = csv_file.readline()
                if line == b'' or line == b'\n':
                    end_of_borehole = True
                    eof = True
                elif (line == b'# markers\n') or (line == b'# markers\t\t\t\t\n') \
                        or (line == b'# markers\r\n') or (line == b'# markers\t\t\t\t\r\n'):
                    end_of_borehole = True
                else:
                    line_descr = [i for i in line.decode('utf-8')[:tl].split('\t')]
                    if line_descr[2] == former_line_descr[2]:
                        del(boreholes[bh_name][(float(former_line_descr[0]), float(former_line_descr[1]))])
                        boreholes[bh_name][(float(former_line_descr[0]), float(line_descr[1]))] = {
                            'description': line_descr[2],
                            'lithology': line_descr[3],
                            'colour': line_descr[4]}
                        former_line_descr = [former_line_descr[0], line_descr[1], line_descr[2], line_descr[3], line_descr[4]]
                    else:
                        boreholes[bh_name][(float(line_descr[0]), float(line_descr[1]))] = {
                            'description': line_descr[2],
                            'lithology': line_descr[3],
                            'colour': line_descr[4]}
                        former_line_descr = line_descr
            if (line == b'# markers\n') or (line == b'# markers\t\t\t\t\n') \
                    or (line == b'# markers\r\n') or (line == b'# markers\t\t\t\t\r\n'):
                line = csv_file.readline()
                boreholes[bh_name]['markers'] = {}
                while line != b'' and line != b'\n' and line != b'\r\n':
                    line_descr = [i for i in line.decode('utf-8')[:tl].split('\t')]
                    boreholes[bh_name]['markers'][line_descr[0]] = float(line_descr[1])
                    line = csv_file.readline()
                eof = True
        return boreholes

