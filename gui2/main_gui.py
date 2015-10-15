import os, sys, datetime, requests
import pickle, gzip, binascii, json
from urlparse import urljoin
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_common import get_database_data, colorwheel

_badDate = datetime.datetime.strptime("January 1, 1000", "%B %d, %Y")

def demo_get_articles(email, password):
    if not os.path.isfile( 'articledata.pkl.gz' ):
        url = urljoin( 'https://tanimislam.ddns.net',
                       '/flask/api/nprstuff/readability/getarticles' )
        response = requests.get( url, auth = ( email, password ) )
        data = json.loads( binascii.a2b_hex( response.json()['data'] ).decode('bz2' ) )
        pickle.dump(data, gzip.open( 'articledata.pkl.gz', 'w') )
        return data
    else:
        return pickle.load( gzip.open( 'articledata.pkl.gz', 'r' ) )

# fix this part here
# self.table.clicked.connect( self.doClickedTable )
def doClickedTable(self, clickedIndex):
    row = clickedIndex.row()
    model = clickedIndex.model()
    act_index = model.index( row, 4 )
    articleId = str( model.data( act_index, Qt.DisplayRole ).toString() )
    
def pushTableData( articles, ordered_ids, tableModel ):
    tabledata = []
    for articleId in ordered_ids:
        artsub = articles[articleId]
        title = titlecase.titlecase( artsub['title'] )
        s_dt = artsub['date_published']
        if s_dt is None:
            dtime = _badDate
            date_string = 'NODATE'
            time_string = 'NOTIME'
        else:
            dtime = datetime.datetime.strptime( s_dt, '%Y-%m-%d %H:%M:%S' )
            date_string = dtime.strftime('%m/%d/%Y')
            time_string = dt.strftime('%H:%M:%S')
        tabledata.append( [ title, date_string, time_string, dtime, articleId ])
    tableModel.pushData( tableData )
            
def create_table_and_model( parent ):
    table = QTableView( parent )
    tm = MyTableModel( parent )
    table.setModel( tm )
    table.setColumnHidden(3, True)
    table.setColumnHidden(4, True)
    table.setItemDelegateForColumn(0, TitleDelegate( parent ) )
    table.setItemDelegateForColumn(1, DateDelegate( parent ) )
    table.setItemDelegateForColumn(2, TimeDelegate( parent ) )

    # set the minimum size
    table.setMinimumSize( 500, 400 )

    # show grid
    table.setShowGrid( True )

    # set fixed vertical headers
    table.verticalHeader().setResizeModel( QHeaderView.Fixed )

    # hide vertical header
    table.verticalHeader().setVisible( False )

    # set sorting enabled
    table.setSortingEnabled( True )

    # other stuff
    table.setSelectionBehavior( QTableView.SelectRows )

    # slots
    tm.layoutChanged.connect( table.resizeColumnsToContents )

    # end button scroll to bottom
    toBotAction = QAction( table )
    toBotAction.setShortcut( 'End' )
    toBotAction.triggered.connect( table.scrollToBottom )
    table.addAction( toBotAction )

    # home button scroll to top
    toTopAction = QAction( table )
    toTopAction.setShortcut( 'Home' )
    toTopAction.triggered.connect( table.scrollToTop )
    table.addAction( toTopAction )
    
    return table, tm

class MyDemoWindow(QWidget):
    def __init__(self):
        super(MyDemoWindow, self).__init__()
        layout = QHBoxLayout()
        self.setLayout( layout )
        

class TitleDelegate(QItemDelegate):
    def __init__(self, owner):
        super(AuthorDelegate, self).__init__(owner)

    def createEditor(self, parent, option, index):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 0 )
        title = str( model.data( act_index, Qt.DisplayRole ).toString() ).strip()
        editor = QLabel( title, parent = parent )
        return editor

    def setEditor(self, editor, index ):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 0 )
        title = str( model.data( act_index, Qt.DisplayRole ).toString() ).strip()
        editor.setText( title )

class DateDelegate(QItemDelegate):
    def __init__(self, owner):
        super(DateDelegate, self).__init__(owner)

    def createEditor(self, parent, option, index):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 3 )
        dtime = model.data( act_index, Qt.DisplayRole).toDateTime().toPyDateTime()
        if dtime == _badDate:
            editor = QLabel("NODATE", parent = parent)
        else:
            editor = QLabel( dtime.strftime( '%m/%d/%Y' ), parent = parent )
        return editor

    def setEditorData(self, editor, index):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 3 )
        dtime = model.data( act_index, Qt.DisplayRole).toDateTime().toPyDateTime()
        if dtime == _badDate:
            editor.setText( "NODATE" )
        else:
            editor.setText( dtime.strftime( "%m/%d/%Y" ) )

class TimeDelegate(QItemDelegate):
    def __init__(self, owner):
        super(TimeDelegate, self).__init__(owner)

    def createEditor(self, parent, option, index):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 3 )
        dtime = model.data( act_index, Qt.DisplayRole).toDateTime().toPyDateTime()
        if dtime == _badDate:
            editor = QLabel("NOTIME", parent = parent)
        else:
            editor = QLabel( dtime.strftime( '%H:%M:%S' ), parent = parent )
        return editor

    def setEditorData(self, editor, index):
        owNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 3 )
        dtime = model.data( act_index, Qt.DisplayRole).toDateTime().toPyDateTime()
        if dtime == _badDate:
            editor.setText( "NOTIME" )
        else:
            editor.setText( dtime.strftime( '%H:%M:%S' ) )

class MyTableModel(QAbstractTableModel):
    def __init__(self, parent = None):
        super(MyTableModel, self).__init__(parent)
        self.arrayData = []
        self.headerData = [ "title", "date" , "time", "datetime", "articleId" ]
        self.myParent = parent

    def pushData(self, tabledata):
        #
        ## first remove all rows that exist
        initRowCount = self.rowCount(None)
        self.beginRemoveRows( QModelIndex(), 0, initRowCount - 1 )
        self.arrayData = []
        self.endRemoveRows( )
        #
        ## now add the rows from tabledata
        self.beginInsertRows( QModelIndex(), 0, len( tabledata ) - 1 )
        self.arrayData = tabledata
        self.endInsertRows( )
        self.sort(0, Qt.AscendingOrder )

    def rowCount(self, parent):
        return len( self.arraydata )

    def columnCount( self, parent ):
        return len( self.headerData )

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.BackgroundRole:
            return QBrush( colorwheel[ index.row() % 6 ] )
        elif role != Qt.DisplayRole:
            return QVariant()
        else:
            return QVariant( self.arraydata[ index.row() ][ index.column() ] )

    def setData( self, index, value, role ):
        if not index.isValid():
            return
        if index.column() in (0, 1, 2, 4):
            self.arraydata[ index.row() ][ index.column() ] = str( value.toString() )
        elif index.column() == 3:
            self.arraydata[ index.row() ][ 3 ] = value.toDateTime().toPyDateTime() 

    def flags( self, index ):
        return Qt.ItemFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled )

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant( self.headerdata[ col ] )
        return QVariant( )

    def sort(self, ncol, order):
        self.layoutAboutToBeChanged.emit()
        self.arraydata = sorted(self.arraydata, key = lambda tup: tup[3] )
        self.layoutChanged.emit()
