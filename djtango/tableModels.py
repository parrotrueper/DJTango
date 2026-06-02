# -*- coding:Utf-8 -*-

from djtango.qt_compat import QAbstractTableModel
from djtango.qt_compat import QSortFilterProxyModel
from djtango.qt_compat import Qt
from djtango.qt_compat import QColor
from djtango.qt_compat import QDataStream, QIODevice, QVariant
import operator, re
from djtango.qt_compat import QRegExp
from djtango import utils
import decimal, random


def get_contrast_color(color):
    luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue())
    return QColor(0, 0, 0) if luminance > 186 else QColor(255, 255, 255)


def get_type_font_color(type_entry):
    if len(type_entry) > 6 and type_entry[6] is not None:
        return QColor(type_entry[6], type_entry[7], type_entry[8], type_entry[9])
    return None


def normalize_type_key(type_key, TYPE):
    if type_key in TYPE:
        return type_key
    if isinstance(type_key, str):
        if type_key.isdigit():
            numeric = int(type_key)
            if numeric in TYPE:
                return numeric
        lowered = type_key.lower()
        for key, value in TYPE.items():
            if len(value) > 1 and isinstance(value[1], str) and value[1].lower() == lowered:
                return key
    return type_key


class library(QAbstractTableModel):
    def __init__(self, parent, mylist, header, TYPE, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
        self.TYPE = TYPE
        
    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0]) if self.mylist else 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        elif role == Qt.BackgroundRole:
            type_key = normalize_type_key(self.mylist[index.row()][5], self.TYPE)
            if type_key in self.TYPE:
                R = self.TYPE[type_key][2]
                G = self.TYPE[type_key][3]
                B = self.TYPE[type_key][4]
                T = self.TYPE[type_key][5]
                return QColor(R, G, B, T)
            return None
        elif role == Qt.ForegroundRole:
            type_key = normalize_type_key(self.mylist[index.row()][5], self.TYPE)
            if type_key in self.TYPE:
                type_entry = self.TYPE[type_key]
                font_color = get_type_font_color(type_entry)
                if font_color is not None:
                    return font_color
                R = type_entry[2]
                G = type_entry[3]
                B = type_entry[4]
                T = type_entry[5]
                return get_contrast_color(QColor(R, G, B, T))
            return None
        elif role != Qt.DisplayRole:
            return None

        if index.column() == 4:
            type_key = normalize_type_key(self.mylist[index.row()][5], self.TYPE)
            if type_key in self.TYPE:
                return self.TYPE[type_key][1].title()
            return "Unknown"
        else:
            return self.mylist[index.row()][index.column()]
    def headerData(self, col, orientation, role):
    	if orientation == Qt.Horizontal and role == Qt.DisplayRole:
    		return self.header[col]
    	if role==Qt.BackgroundRole:
    		return QColor(0,160,176,100)
    	return None

    def sort(self, col, order):
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
        if order != Qt.AscendingOrder:
            self.mylist.reverse()
        self.layoutChanged.emit()
        
    #renew all the data of the table model
    #this can be very time consuming
    def changeData(self, datain):

        self.layoutAboutToBeChanged.emit()
        self.mylist = datain

        self.layoutChanged.emit()
        if self.rowCount(0) > 0 and self.columnCount(0) > 0:
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))

    


    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            self.mylist[index.row()][index.column()] = value
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
            return True
        return False


#=======================================================================
#
#
#
#========================================================================

class milongaSource(QAbstractTableModel):
    def __init__(self, parent, mylist, header, TYPE, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
        self.TYPE = TYPE
        
        
    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        if(len(self.mylist)>0):
            return len(self.mylist[0])
        else:
            return 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        elif role==Qt.BackgroundRole:
            type_key = normalize_type_key(self.mylist[index.row()][5], self.TYPE)
            if type_key in self.TYPE:
                R = self.TYPE[type_key][2]
                G = self.TYPE[type_key][3]
                B = self.TYPE[type_key][4]
                T = self.TYPE[type_key][5]
                return(QColor(R,G,B,T))
            else:
                return None
        elif role==Qt.ForegroundRole:
            type_key = normalize_type_key(self.mylist[index.row()][5], self.TYPE)
            if type_key in self.TYPE:
                type_entry = self.TYPE[type_key]
                font_color = get_type_font_color(type_entry)
                if font_color is not None:
                    return font_color
                R = type_entry[2]
                G = type_entry[3]
                B = type_entry[4]
                T = type_entry[5]
                return get_contrast_color(QColor(R, G, B, T))
            return None
        elif role != Qt.DisplayRole:
            return None
        
        if index.column() == 5:#genre column
            type_key = normalize_type_key(self.mylist[index.row()][5], self.TYPE)
            if type_key in self.TYPE:
                return self.TYPE[type_key][1].title()
            else:
                return "Unknown"
        elif index.column() == 1:
            if self.mylist[index.row()][index.column()] == 0:
                return ''
            else:
                return '>>>'
        elif index.column() == 8:#time column
            time_value = self.mylist[index.row()][index.column()]
            if isinstance(time_value, (int, float)) and time_value < 1000:
                time_value = time_value * 1000
            return utils.msecToms(time_value)
        elif index.column() == 7: #bpm column
            return ('%.2f' % float(self.mylist[index.row()][index.column()]))
        else:
            return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        if role==Qt.BackgroundRole:
            return QColor(0,160,176,100)
        return None

    def sort(self, col, order):
        self.layoutAboutToBeChanged.emit()
        self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
        if order == Qt.AscendingOrder:
            self.mylist.reverse()
        self.layoutChanged.emit()
    def randomize(self):

        self.layoutAboutToBeChanged.emit()
        random.shuffle(self.mylist)
        self.layoutChanged.emit()

    def changeData(self, datain):
        self.layoutAboutToBeChanged.emit()
        self.mylist = datain
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))

    #will add some data at the end of the table, updating the model at this point
    def addNewData(self, datas):

        self.layoutAboutToBeChanged.emit()
        for data in datas:
            self.mylist.append(data)
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(self.rowCount(0)-len(datas), self.columnCount(0)-len(datas)), self.createIndex(self.rowCount(0), self.columnCount(0)))
        
    def setData(self, index, value, role):

        if index.isValid() and role == Qt.EditRole:
            self.mylist[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False
    def flags(self, index):
        return Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def removeRows(self, row, count, parent):
        
        self.beginRemoveRows(parent, row, row+count-1);
        self.endRemoveRows()
        return True

#=======================================================================
#
#
#
#========================================================================

#=======================================================================
#
#
#
#========================================================================

class milongaDest(QAbstractTableModel):
    def __init__(self, parent, mylist, header, TYPE, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
        self.TYPE = TYPE
        self.invertTYPE = self.invert(TYPE)
        self.startingRow=0
        
    def invert(self, TYPE):
        ret={}
        for key, value in TYPE.items():
            # map title-cased genre labels back to numeric type keys
            ret[value[1].title()] = key
        return ret
    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        elif role==Qt.BackgroundRole:
            R = self.TYPE[self.mylist[index.row()][5]][2]
            G = self.TYPE[self.mylist[index.row()][5]][3]
            B = self.TYPE[self.mylist[index.row()][5]][4]
            T = self.TYPE[self.mylist[index.row()][5]][5]
            return(QColor(R,G,B,T))
        elif role==Qt.ForegroundRole:
            type_entry = self.TYPE[self.mylist[index.row()][5]]
            font_color = get_type_font_color(type_entry)
            if font_color is not None:
                return font_color
            R = type_entry[2]
            G = type_entry[3]
            B = type_entry[4]
            T = type_entry[5]
            return get_contrast_color(QColor(R, G, B, T))
        elif role != Qt.DisplayRole:
            return None
        
        if index.column() == 5:
            return self.TYPE[self.mylist[index.row()][5]][1].title()
        elif index.column() == 1:
            if self.mylist[index.row()][index.column()] == 0:
                return ''
            else:
                return '>>>'
        elif index.column() == 8:#time column
            if (self.mylist[index.row()][5] == 4):
                return "-"
            time_value = self.mylist[index.row()][index.column()]
            if isinstance(time_value, (int, float)) and time_value < 1000:
                time_value = time_value * 1000
            return utils.msecToms(time_value)
        elif index.column() == 7: #bpm column
            return ('%.2f' % float(self.mylist[index.row()][index.column()]))
        else:
            return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        if role==Qt.BackgroundRole:
            return QColor(0,160,176,100)
        return None

    def changeData(self, datain):
        self.layoutAboutToBeChanged.emit()
        self.mylist = datain
        
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            self.mylist[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False
    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDropEnabled 

    def dropMimeData(self, data, action, row, column, parent):

        self.layoutAboutToBeChanged.emit()
        if action == Qt.IgnoreAction:
            return True

        if not data.hasFormat("application/x-qabstractitemmodeldatalist"):
            return False


        beginRow = -1

        if not row == -1:
            beginRow = row;
        elif parent.isValid():
            beginRow = parent.row()
        else:
            beginRow = self.rowCount(self)


        encodedData = data.data("application/x-qabstractitemmodeldatalist")
        data_items = self.decode_data(encodedData)

        lineNB = int(len(data_items)/self.columnCount(parent))



        if action == Qt.MoveAction:
            self.moveRow(self.startingRow,beginRow, parent)
        else:
            beginRow +=1
            if beginRow <= self.rowCount(self): curRow = 0
            else: curRow = -1

            for i in range(0, lineNB):
                self.insertRow(beginRow+i, parent)

            col = 0
            rowItem={}

            for data in data_items:
                if data['row'] not in rowItem.keys():
                    rowItem[data['row']] = data['row']


            for key in sorted(rowItem.keys()):
                rowItem[key] = curRow
                curRow+=1


            for data in data_items:
                if data['column'] == 5:
                    normalized = normalize_type_key(data[0], self.TYPE)
                    if normalized in self.TYPE:
                        data[0] = normalized
                if data['column'] == 1:
                    data[0] = 0

                idx = self.index(beginRow+rowItem[data['row']], data['column'], parent);
                self.setData(idx, data[0], Qt.EditRole);
                
                col+=1
    
            self.layoutChanged.emit()
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        return True

    def supportedDropActions(self):
        return Qt.MoveAction | Qt.CopyAction

    def pressed(self, index):
        self.startingRow = index.row()

    def moveRow(self, start, end, parent):
        tmp = self.mylist[start]
        if end == self.rowCount(parent):
            self.insertRow(end,parent)
            self.mylist[end] = tmp[:]    
        else:
            self.insertRow(end+1,parent)
            self.mylist[end+1] = tmp[:]    
        
        if start>end:
            self.removeRows(start+1,1,parent)
        else:
            self.removeRows(start,1,parent)

        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))

    def insertRow(self, row, parent):

        before = self.mylist[:row]
        after = self.mylist[row:]
        line =[0]*len(self.header)
        if len(self.mylist) == 0 or len(after) == 0 :
            self.mylist.append(line)
        else:
            self.mylist = before[:]
            self.mylist.append(line)
            self.mylist.extend(after)
        return True

    def removeRows(self, row, count, parent):
        
        self.beginRemoveRows(parent, row, count);

        before = self.mylist[:row]
        after = self.mylist[row+count:]
        
        if len(before) == 0:
            self.mylist = after[:]
        elif len(after) == 0:
            self.mylist = before[:]
        else: 
            self.mylist = before[:]
            self.mylist.extend(after)

        #
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        return True
    

    def decode_data(self, encodedData):
        data = []
        item = {}
        ds = QDataStream(encodedData, QIODevice.ReadOnly)
        while not ds.atEnd():
        
            row = ds.readInt32()
            column = ds.readInt32()
            map_items = ds.readInt32()
            item = {}
            for i in range(map_items):
                key = ds.readInt32()
                item[Qt.ItemDataRole(key)] = ds.readQVariant()
                item['row'] = row
                item['column'] = column
            data.append(item)
        return data



class sourceFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent):
        QSortFilterProxyModel.__init__(self, parent)
        self.artistRegExp = re.compile('.*', re.IGNORECASE)
        self.albumRegExp = re.compile('.*', re.IGNORECASE)
        self.genreRegExp = re.compile('.*', re.IGNORECASE)
        self.allRegExp = re.compile('.*', re.IGNORECASE)
        self.linefilter = '.*'


    def filterAcceptsRow(self, sourceRow, parent):
        ret = True
        indexArtist = self.sourceModel().index(sourceRow, 3, parent)
        indexAlbum = self.sourceModel().index(sourceRow, 4, parent)
        indexGenre = self.sourceModel().index(sourceRow, 5, parent)


        resArtist = self.artistRegExp.match(self.sourceModel().data(indexArtist))
        resAlbum = self.albumRegExp.match(self.sourceModel().data(indexAlbum))
        resGenre = self.genreRegExp.match(self.sourceModel().data(indexGenre))

        if self.linefilter == '.*':
            retAllfilter = 'YES'
        else:
            retAllfilter = None

            for i in range(0,7):
                index = self.sourceModel().index(sourceRow, i, parent)
                retLineFilter = self.allRegExp.match(str(self.sourceModel().data(index)))
                if retLineFilter is not None:
                    retAllfilter = 'YES'
        




        if resArtist is None or resAlbum is None or resGenre is None or retAllfilter is None:
            ret = False

        return ret
        
    def setlFilterValues(self, artistExp, albumExp, genreExp, linefilter):
        self.artistRegExp = re.compile('.*'+artistExp+'.*', re.IGNORECASE)
        self.albumRegExp = re.compile('.*'+albumExp+'.*', re.IGNORECASE)
        self.genreRegExp = re.compile('.*'+genreExp+'.*', re.IGNORECASE)
        self.allRegExp = re.compile('.*'+linefilter+'.*', re.IGNORECASE)
        self.linefilter = linefilter


        self.setFilterKeyColumn(0)  

    def sort(self, col, order):
        self.sourceModel().sort(col, order)
