import psycopg2
import sys
from datetime import date
from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QAbstractScrollArea, QVBoxLayout, QHBoxLayout, QTableWidget, QGroupBox, QTableWidgetItem, QPushButton, QMessageBox, QInputDialog)

#проверка чётности недели: если неделя чётная, то одно расписание, в противном случае другое
today = date.today()
num = int(today.isocalendar().week)
if (num % 2) == 0:
    this_week = "timetable_week2"
else:
    this_week = "timetable_week1"
#
#создаётся окно
class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self._connect_to_db() #подключение к БД

        self.setWindowTitle("BVT2205 Information") #назначается название окна

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self._create_schedule_tab()
        self._create_teacher_tab()
        self._create_timetable_week1_tab()
        self._create_timetable_week2_tab()

        self.rowSelected = None
        self.idSelected = None

    # connect to db
    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="lab8",
                                     user="postgres",
                                     password="K89164466539k!",
                                     host="localhost",
                                     port="5432")

        self.cursor = self.conn.cursor()






    # define teacher tab
    def _create_teacher_tab(self):
        self.teacher_tab = QWidget()
        self.tabs.addTab(self.teacher_tab, "Teacher")

        self.teacher_gbox = QGroupBox("Teacher")

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.teacher_gbox)

        self._create_teacher_table()

        self.update_teacher_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_teacher_button)
        self.update_teacher_button.clicked.connect(self._update_teacher)

        self.shboxa = QHBoxLayout()
        self.shbox1.addLayout(self.shboxa)
        self.alter_teacher_button = QPushButton("Alter")
        self.shboxa.addWidget(self.alter_teacher_button)
        self.alter_teacher_button.clicked.connect(lambda ch: self.update_teacher_info('Alter'))

        self.shboxd = QHBoxLayout()
        self.shbox1.addLayout(self.shboxd)
        self.delete_teacher_button = QPushButton("Delete")
        self.shboxd.addWidget(self.delete_teacher_button)
        self.delete_teacher_button.clicked.connect(lambda ch: self.update_teacher_info('Delete'))

        self.shboxrow = QHBoxLayout()
        self.shbox1.addLayout(self.shboxrow)
        self.add_teacher_button = QPushButton("Add Row")
        self.shboxrow.addWidget(self.add_teacher_button)
        self.add_teacher_button.clicked.connect(lambda ch: self.update_teacher_info('Add Row'))

        self.teacher_tab.setLayout(self.svbox)

    # display teacher table
    def _create_teacher_table(self):
        self.teacher_table = QTableWidget()
        self.teacher_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.teacher_table.setColumnCount(3)
        self.teacher_table.setHorizontalHeaderLabels(["Full Name", "Subject", ""])

        self._update_teacher_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.teacher_table)
        self.teacher_gbox.setLayout(self.mvbox)

    # create and fill teacher table
    def _update_teacher_table(self):
        self.cursor.execute("SELECT * FROM teacher")
        records = list(self.cursor.fetchall())

        self.teacher_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            updateTeach = QPushButton("Select")

            self.teacher_table.setItem(i, 0,
                                       QTableWidgetItem(str(r[1])))
            self.teacher_table.setItem(i, 1,
                                       QTableWidgetItem(str(r[2])))
            self.teacher_table.setItem(len(records), 0, QTableWidgetItem(str('')))
            self.teacher_table.setItem(len(records), 1, QTableWidgetItem(str('')))

            self.teacher_table.setCellWidget(i, 2, updateTeach)
            updateTeach.clicked.connect(lambda ch, num=i, id=r[0]: self.select_row(num, id))

        selectTeach = QPushButton("Select")
        self.teacher_table.setCellWidget(len(records),2, selectTeach)
        selectTeach.clicked.connect(lambda ch, num=len(records): self.select_row(num))

        self.teacher_table.resizeRowsToContents()

    def update_teacher_info(self, query):
        if query == 'Alter':
            self.cursor.execute("select count(full_name) from teacher")
            records = self.cursor.fetchall()
            #print (self.rowSelected)
            try:
                if records[0][0] == self.rowSelected:
                    raise Exception
                elif records[0][0] > self.rowSelected:
                    self.cursor.execute("SELECT column_name FROM information_schema.columns "
                                        "WHERE table_schema = 'public' AND table_name = 'teacher' ")
                    columns = self.cursor.fetchall()
                    new_values = []
                    for temp in columns[1:]:
                        text, ok = QInputDialog.getText(self, 'Add new teacher', 'Enter {} value:'.format(temp[0]))
                        if ok and text != "":
                            new_values.append(text)
                    if len(new_values) == 2:
                        try:
                            self.cursor.execute("update teacher "
                                                "set full_name = %s, subject = %s "
                                                "where id = {};".format(self.idSelected), tuple(new_values))
                            self.conn.commit()
                        except:
                            self.conn.commit()
                            QMessageBox.about(self, "Error", "Given subject value "
                                                             "does not exist in subject table")

            except:
                self.conn.commit()
                QMessageBox.about(self, "Error", "Select a non empty row first")

        elif query == 'Delete':
            self.cursor.execute("select count(full_name) from teacher")
            records = self.cursor.fetchall()
#            print (self.rowSelected)
            try:
                if records[0][0] == self.rowSelected:
                    raise Exception
                elif records[0][0] > self.rowSelected:
                    print(self.rowSelected)
                    self.cursor.execute("delete from teacher where id={}".format(self.idSelected))
                    self.conn.commit()
            except:
                self.conn.commit()
                QMessageBox.about(self, "Error", "Select a non empty row first")

        elif query == 'Add Row':
            self.cursor.execute("select count(full_name) from teacher")
            records = self.cursor.fetchall()
            if records[0][0] == self.rowSelected:
                print('Can do')
                self.cursor.execute("SELECT column_name FROM information_schema.columns "
                                    "WHERE table_schema = 'public' AND table_name = 'teacher' ")
                columns = self.cursor.fetchall()
                new_values = []
                for temp in columns[1:]:
                    text, ok = QInputDialog.getText(self, 'Add new teacher', 'Enter {} value:'.format(temp[0]))
                    if ok and text != "":
                        new_values.append(text)
                if len(new_values) == 2:
                    try:
                        self.cursor.execute("insert into "
                                            "teacher (full_name, subject) "
                                            "values (%s, %s);", tuple(new_values))
                        self.conn.commit()
                    except:
                        self.conn.commit()
                        QMessageBox.about(self, "Error", "Given subject value "
                                                         "does not exist in subject table")

                print(new_values)

            else:
                QMessageBox.about(self, "Error", "Select an empty row first")

    def _update_teacher(self):
        self.rowSelected = None
        self.idSelected = None
        self._update_teacher_table()


    # display timetable week1
    def _create_timetable_week1_tab(self):
        self.timetable_week1_tab = QWidget()
        self.tabs.addTab(self.timetable_week1_tab, "Week1")

        self.timetable_week1_gbox = QGroupBox("Week1")

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.timetable_week1_gbox)

        self._create_timetable_week1_table()

        self.update_timetable_week1_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_timetable_week1_button)
        self.update_timetable_week1_button.clicked.connect(self._update_timetable_week1)

        self.timetable_week1_tab.setLayout(self.svbox)

    # display timetable week1
    def _create_timetable_week1_table(self):
        self.timetable_week1_table = QTableWidget()
        self.timetable_week1_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.timetable_week1_table.setColumnCount(2)
        self.timetable_week1_table.setHorizontalHeaderLabels(["Day", "Lessons", ""])

        self._update_timetable_week1_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.timetable_week1_table)
        self.timetable_week1_gbox.setLayout(self.mvbox)

    # define display timetable week1
    def _update_timetable_week1_table(self):
        self.cursor.execute(
            "select day, string_agg(table_column, '\n\n') as table_row from (select day, timetable_week1.subject ||' | '|| room_numb ||' | '|| start_time ||'-'|| finish_time ||' | '|| full_name as table_column from timetable_week1, teacher where teacher.subject = timetable_week1.subject order by start_time)timetable_week1 group by 1 order by case when day = 'Monday' then 1 when day = 'Tuesday' then 2 when day = 'Wednesday' then 3 when day = 'Thursday' then 4 else 5 end;")
        records = list(self.cursor.fetchall())

        self.timetable_week1_table.setRowCount(len(records))

        for i, r in enumerate(records):
            r = list(r)

            self.timetable_week1_table.setItem(i, 0,
                                               QTableWidgetItem(str(r[0])))
            self.timetable_week1_table.setItem(i, 1,
                                               QTableWidgetItem(str(r[1])))

        self.timetable_week1_table.resizeRowsToContents()

    def _update_timetable_week1(self):
        self.rowSelected = None
        self.idSelected = None
        self._update_timetable_week1_table()


    # display timetable week2
    def _create_timetable_week2_tab(self):
        self.timetable_week2_tab = QWidget()
        self.tabs.addTab(self.timetable_week2_tab, "Week2")

        self.timetable_week2_gbox = QGroupBox("Week2")

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.timetable_week2_gbox)

        self._create_timetable_week2_table()

        self.update_timetable_week2_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_timetable_week2_button)
        self.update_timetable_week2_button.clicked.connect(self._update_timetable_week2)

        self.timetable_week2_tab.setLayout(self.svbox)

    # display timetable week2
    def _create_timetable_week2_table(self):
        self.timetable_week2_table = QTableWidget()
        self.timetable_week2_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.timetable_week2_table.setColumnCount(2)
        self.timetable_week2_table.setHorizontalHeaderLabels(["Day", "Lessons", ""])

        self._update_timetable_week2_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.timetable_week2_table)
        self.timetable_week2_gbox.setLayout(self.mvbox)

    # define display timetable week2
    def _update_timetable_week2_table(self):
        self.cursor.execute(
            "select day, string_agg(table_column, '\n\n') as table_row from (select day, timetable_week2.subject ||' | '|| room_numb ||' | '|| start_time ||'-'|| finish_time ||' | '|| full_name as table_column from timetable_week2, teacher where teacher.subject = timetable_week2.subject order by start_time)timetable_week2 group by 1 order by case when day = 'Monday' then 1 when day = 'Tuesday' then 2 when day = 'Wednesday' then 3 when day = 'Thursday' then 4 else 5 end;")
        records = list(self.cursor.fetchall())

        self.timetable_week2_table.setRowCount(len(records))

        for i, r in enumerate(records):
            r = list(r)

            self.timetable_week2_table.setItem(i, 0,
                                               QTableWidgetItem(str(r[0])))
            self.timetable_week2_table.setItem(i, 1,
                                               QTableWidgetItem(str(r[1])))

        self.timetable_week2_table.resizeRowsToContents()

    def _update_timetable_week2(self):
        self.rowSelected = None
        self.idSelected = None
        self._update_timetable_week2_table()


    # display timetable tab by days
    def _create_schedule_tab(self):
        self.day = 'Monday'
        self.schedule_tab = QWidget()
        self.tabs.addTab(self.schedule_tab, "Schedule")

        self.schedule_gbox = QGroupBox("{}".format(self.day))

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)

        self.shbox1.addWidget(self.schedule_gbox)

        self._create_schedule_table()

        self.svbox.addLayout(self.shbox2)
        self.update_schedule_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_schedule_button)
        self.update_schedule_button.clicked.connect(self._update_schedule)

        self.shboxm = QHBoxLayout()
        self.svbox.addLayout(self.shboxm)
        self.monday_schedule_button = QPushButton("Monday")
        self.shboxm.addWidget(self.monday_schedule_button)
        self.monday_schedule_button.clicked.connect(lambda ch: self.btnstate('Monday'))

        self.shboxt = QHBoxLayout()
        self.shboxm.addLayout(self.shboxt)
        self.tuesday_schedule_button = QPushButton("Tuesday")
        self.shboxt.addWidget(self.tuesday_schedule_button)
        self.tuesday_schedule_button.clicked.connect(lambda ch: self.btnstate('Tuesday'))

        self.shboxw = QHBoxLayout()
        self.shboxm.addLayout(self.shboxw)
        self.wednesday_schedule_button = QPushButton("Wednesday")
        self.shboxw.addWidget(self.wednesday_schedule_button)
        self.wednesday_schedule_button.clicked.connect(lambda ch: self.btnstate('Wednesday'))

        self.shboxth = QHBoxLayout()
        self.shboxm.addLayout(self.shboxth)
        self.thursday_schedule_button = QPushButton("Thursday")
        self.shboxth.addWidget(self.thursday_schedule_button)
        self.thursday_schedule_button.clicked.connect(lambda ch: self.btnstate('Thursday'))

        self.shboxf = QHBoxLayout()
        self.shboxm.addLayout(self.shboxf)
        self.friday_schedule_button = QPushButton("Friday")
        self.shboxf.addWidget(self.friday_schedule_button)
        self.friday_schedule_button.clicked.connect(lambda ch: self.btnstate('Friday'))

        self.shboxa = QHBoxLayout()
        self.shbox1.addLayout(self.shboxa)
        self.alter_lesson_button = QPushButton("Alter")
        self.shboxa.addWidget(self.alter_lesson_button)
        self.alter_lesson_button.clicked.connect(lambda ch: self.update_lesson('Alter'))

        self.shboxd = QHBoxLayout()
        self.shbox1.addLayout(self.shboxd)
        self.delete_lesson_button = QPushButton("Delete")
        self.shboxd.addWidget(self.delete_lesson_button)
        self.delete_lesson_button.clicked.connect(lambda ch: self.update_lesson('Delete'))

        self.shboxrow = QHBoxLayout()
        self.shbox1.addLayout(self.shboxrow)
        self.add_row_button = QPushButton("Add Row")
        self.shboxrow.addWidget(self.add_row_button)
        self.add_row_button.clicked.connect(lambda ch: self.update_lesson('Add Row'))

        self.schedule_tab.setLayout(self.svbox)

    # display schedule for the day
    def _create_schedule_table(self):
        self.schedule_table = QTableWidget()
        self.schedule_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels(["Subject", "Room numb", "Start time", "Finish time", "", ""])

        self._update_schedule_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.schedule_table)
        self.schedule_gbox.setLayout(self.mvbox)

    def btnstate(self, wday):
        self.day = wday

    def _update_schedule_table(self):
        self.cursor.execute(
            "SELECT subject, room_numb, start_time, finish_time, id FROM {} WHERE day = '{}'".format(this_week, self.day))
        records = list(self.cursor.fetchall())

        self.schedule_table.setRowCount(len(records) + 1)
        self.schedule_gbox.setTitle(self.day)
        for i, r in enumerate(records):
            r = list(r)
            #            updateButton = QPushButton("Update")
            #            deleteButton = QPushButton("Delete")
            #            addRow = QPushButton("Add Row")
            selectRow = QPushButton("Select")

            self.schedule_table.setItem(i, 0,
                                        QTableWidgetItem(str(r[0])))
            self.schedule_table.setItem(i, 1,
                                        QTableWidgetItem(str(r[1])))
            self.schedule_table.setItem(i, 2,
                                        QTableWidgetItem(str(r[2])))
            self.schedule_table.setItem(i, 3,
                                        QTableWidgetItem(str(r[3])))
            self.schedule_table.setItem(len(records), 0, QTableWidgetItem(str('')))
            self.schedule_table.setItem(len(records), 1, QTableWidgetItem(str('')))
            self.schedule_table.setItem(len(records), 2, QTableWidgetItem(str('')))
            self.schedule_table.setItem(len(records), 3, QTableWidgetItem(str('')))

            self.schedule_table.setCellWidget(i, 4, selectRow)
            selectRow.clicked.connect(lambda ch, num=i, id=r[4]: self.select_row(num, id))
        selectRow = QPushButton("Select")
        self.schedule_table.setCellWidget(len(records), 4, selectRow)
        selectRow.clicked.connect(lambda ch, num=len(records): self.select_row(num))

        self.schedule_table.resizeRowsToContents()



    def select_row(self, numRow, *numId):
        self.rowSelected = numRow
        if numId:
            self.idSelected = numId[0]
            print (self.idSelected)
        print (self.rowSelected)

    def update_lesson(self, query):
        if query == 'Alter':
            print('alter')
            self.cursor.execute("select count(day) from {} where day = %s".format(this_week), (self.day,))
            records = self.cursor.fetchall()
            print (self.rowSelected)
            try:
                if records[0][0] == self.rowSelected:
                    raise Exception
                elif records[0][0] > self.rowSelected:
                    new_values = []
                    self.cursor.execute("SELECT column_name FROM information_schema.columns "
                                        "WHERE table_schema = 'public' AND table_name = '{}' ".format(this_week))
                    columns = self.cursor.fetchall()
                    for temp in columns[2:]:
                        text, ok = QInputDialog.getText(self, 'Alter in timetable', 'Enter {} value:'.format(temp[0]))
                        if ok and text != "":
                            new_values.append(text)
                    if len(new_values) == 4:
                        try:
                            print(new_values)
                            self.cursor.execute("update {} set subject = %s, room_numb= %s, start_time = %s, finish_time = %s where id= {}".format(this_week, self.idSelected), tuple(new_values))
                            self.conn.commit()
                        except:
                            self.conn.commit()
                            QMessageBox.about(self, "Error", "Given subject value "
                                                         "does not exist in subject table")

            except:
                self.conn.commit()
                QMessageBox.about(self, "Error", "Select a non empty row first")

        elif query == 'Delete':
            self.cursor.execute("select count(day) from {} where day = %s".format(this_week), (self.day,))
            records = self.cursor.fetchall()
            print (self.rowSelected)
            try:
                if records[0][0] == self.rowSelected:
                    raise Exception
                elif records[0][0] > self.rowSelected:
                    self.cursor.execute("delete from {} where id={}".format(this_week, self.idSelected))
                    self.conn.commit()
            except:
                self.conn.commit()
                QMessageBox.about(self, "Error", "Select a non empty row first")

        elif query == 'Add Row':
            self.cursor.execute("select count(day) from {} where day = %s".format(this_week), (self.day,))
            records = self.cursor.fetchall()
            if records[0][0] == self.rowSelected:
                print('Can do')
                self.cursor.execute("SELECT column_name FROM information_schema.columns "
                                    "WHERE table_schema = 'public' AND table_name = '{}' ".format(this_week))
                columns = self.cursor.fetchall()
                new_values = [self.day]
                for temp in columns[2:]:
                    text, ok = QInputDialog.getText(self, 'Add in timetable', 'Enter {} value:'.format(temp[0]))
                    if ok and text != "":
                        new_values.append(text)
                if len(new_values) == 5:
                    try:
                        self.cursor.execute("insert into "
                                            "{}(day, subject, room_numb, start_time, finish_time) "
                                            "values (%s, %s, %s, %s, %s);".format(this_week), tuple(new_values))
                        self.conn.commit()
                    except:
                        self.conn.commit()
                        QMessageBox.about(self, "Error", "Given subject value "
                                                         "does not exist in subject table")

                print(new_values)

            else:
                QMessageBox.about(self, "Error", "Select an empty row first")

    def _update_schedule(self):
        self.rowSelected = None
        self.idSelected = None
        self._update_schedule_table()



app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())