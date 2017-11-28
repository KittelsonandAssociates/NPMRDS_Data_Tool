from PyQt5 import QtWidgets
from stat_func import create_et_analysis, create_speed_band, create_travel_time_cdf, create_speed_freq
from chart_defaults import ChartOptions, AnalysisOptions
from mpl_panels import create_spacer_line
from mpl_charts import MplChart


class Stage2GridPanel(QtWidgets.QWidget):
    def __init__(self, project, chart_options=None, analysis_options=None):
        QtWidgets.QWidget.__init__(self)

        self.f_extra_time = create_et_analysis
        self.f_speed_band = create_speed_band
        self.f_tt_cdf = create_travel_time_cdf
        self.f_speed_freq = create_speed_freq

        self.chart11 = None
        self.chart21 = None
        self.chart12 = None
        self.chart22 = None
        self.panel_col1 = QtWidgets.QWidget(self)
        self.panel_col2 = QtWidgets.QWidget(self)
        self.chart_panel = QtWidgets.QWidget(self)
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.grid_layout = QtWidgets.QGridLayout(self.chart_panel)

        self.init_mode = True
        self.project = project
        df = self.project.database.get_data()
        dr1 = self.project.get_date_range(0)
        df_period1 = df[(df['Date'] >= dr1[0].toString('yyyy-MM-dd')) & (df['Date'] <= dr1[1].toString('yyyy-MM-dd'))]
        dr2 = self.project.get_date_range(1)
        df_period2 = df[(df['Date'] > dr2[0].toString('yyyy-MM-dd')) & (df['Date'] < dr2[1].toString('yyyy-MM-dd'))]
        self.period1 = dr1[0].toString('yyyy-MM-dd') + ' to ' + dr1[1].toString('yyyy-MM-dd')
        self.period2 = dr2[0].toString('yyyy-MM-dd') + ' to ' + dr2[1].toString('yyyy-MM-dd')
        tmc = self.project.database.get_tmcs()
        self.facility_len = tmc['miles'].sum()
        self.dfs = [df_period1, df_period2]
        # self.dfs = [self.f_extra_time(df) for df in self.dfs]
        # self.dfs = [self.f_extra_time(df_period1), self.f_extra_time(df_period2)]
        # self.tmc_subset = []
        # self.facility_len_subset = tmc[tmc['tmc'].isin(self.tmc_subset)]['miles'].sum()
        tmc = self.project.get_tmc()
        self.selected_tmc_name = tmc['tmc'][0]
        self.selected_tmc_len = tmc['miles'][0]
        self.available_days = self.project.database.get_available_days()
        self.plot_days = self.available_days.copy()
        if chart_options is not None:
            self.chart_options = chart_options
        else:
            self.chart_options = ChartOptions()

        if analysis_options is not None:
            self.analysis_options = analysis_options
        else:
            self.analysis_options = AnalysisOptions()

        self.chart_options.chart_type[0][0] = 100
        self.chart_options.chart_type[0][1] = 102
        self.chart_options.chart_type[1][0] = 101
        self.chart_options.chart_type[1][1] = 103

        # Filter Components
        self.cb_tmc_select = QtWidgets.QComboBox()
        self.cb_tmc_select.addItems(self.project.get_tmc(as_list=True))
        # self.check_wkdy = QtWidgets.QCheckBox('Weekdays')
        # self.check_wknd = QtWidgets.QCheckBox("Weekends")
        # self.check_mon = QtWidgets.QCheckBox('Mon')
        # self.check_tue = QtWidgets.QCheckBox('Tue')
        # self.check_wed = QtWidgets.QCheckBox('Wed')
        # self.check_thu = QtWidgets.QCheckBox('Thu')
        # self.check_fri = QtWidgets.QCheckBox('Fri')
        # self.check_sat = QtWidgets.QCheckBox('Sat')
        # self.check_sun = QtWidgets.QCheckBox('Sun')
        self.bg_day_select = QtWidgets.QButtonGroup(self)
        self.check_wkdy = QtWidgets.QRadioButton('Weekdays')
        self.check_wknd = QtWidgets.QRadioButton("Weekends")
        self.check_mon = QtWidgets.QRadioButton('Mon')
        self.check_tue = QtWidgets.QRadioButton('Tue')
        self.check_wed = QtWidgets.QRadioButton('Wed')
        self.check_thu = QtWidgets.QRadioButton('Thu')
        self.check_fri = QtWidgets.QRadioButton('Fri')
        self.check_sat = QtWidgets.QRadioButton('Sat')
        self.check_sun = QtWidgets.QRadioButton('Sun')
        self.bg_day_select.addButton(self.check_wkdy)
        self.bg_day_select.addButton(self.check_wknd)
        self.bg_day_select.addButton(self.check_mon)
        self.bg_day_select.addButton(self.check_tue)
        self.bg_day_select.addButton(self.check_wed)
        self.bg_day_select.addButton(self.check_thu)
        self.bg_day_select.addButton(self.check_fri)
        self.bg_day_select.addButton(self.check_sat)
        self.bg_day_select.addButton(self.check_sun)
        self.check_bar_day = QtWidgets.QWidget(self)
        self.h_layout = QtWidgets.QHBoxLayout(self.check_bar_day)
        self.h_layout.addWidget(self.cb_tmc_select)
        self.h_layout.addWidget(create_spacer_line(self))
        self.h_layout.addWidget(self.check_wkdy)
        self.h_layout.addWidget(self.check_wknd)
        self.h_layout.addWidget(create_spacer_line(self))
        self.h_layout.addWidget(self.check_mon)
        self.h_layout.addWidget(self.check_tue)
        self.h_layout.addWidget(self.check_wed)
        self.h_layout.addWidget(self.check_thu)
        self.h_layout.addWidget(self.check_fri)
        self.h_layout.addWidget(self.check_sat)
        self.h_layout.addWidget(self.check_sun)
        # self.connect_check_boxes()
        self.connect_radio_buttons()
        self.connect_combo_boxes()

        self.day_select = 0
        self.plot_dfs = []
        print('here-1')
        self.update_plot_data()
        print('here0')
        self.create_charts()
        print('here1')
        self.add_charts_to_layouts()
        print('here2')
        self.v_layout.addWidget(self.chart_panel)
        print('here3')
        self.v_layout.addWidget(self.check_bar_day)
        print('here4')
        self.update_chart_visibility()
        print('here5')
        self.init_mode = False
        self.no_compute = False

    def update_plot_data(self, **kwargs):
        # self.plot_dfs = [self.f_extra_time(df[df['weekday'].isin(self.plot_days)]) for df in self.dfs]
        before_df = self.dfs[0]
        after_df = self.dfs[1]
        self.plot_dfs = [self.f_extra_time(before_df[before_df['weekday'].isin([0, 1, 2, 3, 4])]),
                         self.f_extra_time(before_df[before_df['weekday'].isin([5, 6])]),
                         self.f_extra_time(before_df[before_df['weekday'].isin([0])]),
                         self.f_extra_time(before_df[before_df['weekday'].isin([1])]),
                         self.f_extra_time(before_df[before_df['weekday'].isin([2])]),
                         self.f_extra_time(before_df[before_df['weekday'].isin([3])]),
                         self.f_extra_time(before_df[before_df['weekday'].isin([4])]),
                         self.f_extra_time(before_df[before_df['weekday'].isin([5])]),
                         self.f_extra_time(before_df[before_df['weekday'].isin([6])]),
                         self.f_extra_time(after_df[after_df['weekday'].isin([0, 1, 2, 3, 4])]),
                         self.f_extra_time(after_df[after_df['weekday'].isin([5, 6])]),
                         self.f_extra_time(after_df[after_df['weekday'].isin([0])]),
                         self.f_extra_time(after_df[after_df['weekday'].isin([1])]),
                         self.f_extra_time(after_df[after_df['weekday'].isin([2])]),
                         self.f_extra_time(after_df[after_df['weekday'].isin([3])]),
                         self.f_extra_time(after_df[after_df['weekday'].isin([4])]),
                         self.f_extra_time(after_df[after_df['weekday'].isin([5])]),
                         self.f_extra_time(after_df[after_df['weekday'].isin([6])])
                         ]

        self.plot_dfs2 = [self.f_speed_band(before_df[before_df['weekday'].isin([0, 1, 2, 3, 4])]),
                         self.f_speed_band(before_df[before_df['weekday'].isin([5, 6])]),
                         self.f_speed_band(before_df[before_df['weekday'].isin([0])]),
                         self.f_speed_band(before_df[before_df['weekday'].isin([1])]),
                         self.f_speed_band(before_df[before_df['weekday'].isin([2])]),
                         self.f_speed_band(before_df[before_df['weekday'].isin([3])]),
                         self.f_speed_band(before_df[before_df['weekday'].isin([4])]),
                         self.f_speed_band(before_df[before_df['weekday'].isin([5])]),
                         self.f_speed_band(before_df[before_df['weekday'].isin([6])]),
                         self.f_speed_band(after_df[after_df['weekday'].isin([0, 1, 2, 3, 4])]),
                         self.f_speed_band(after_df[after_df['weekday'].isin([5, 6])]),
                         self.f_speed_band(after_df[after_df['weekday'].isin([0])]),
                         self.f_speed_band(after_df[after_df['weekday'].isin([1])]),
                         self.f_speed_band(after_df[after_df['weekday'].isin([2])]),
                         self.f_speed_band(after_df[after_df['weekday'].isin([3])]),
                         self.f_speed_band(after_df[after_df['weekday'].isin([4])]),
                         self.f_speed_band(after_df[after_df['weekday'].isin([5])]),
                         self.f_speed_band(after_df[after_df['weekday'].isin([6])])
                         ]

        self.plot_dfs3 = [self.f_tt_cdf(before_df[before_df['weekday'].isin([0, 1, 2, 3, 4])]),
                          self.f_tt_cdf(before_df[before_df['weekday'].isin([5, 6])]),
                          self.f_tt_cdf(before_df[before_df['weekday'].isin([0])]),
                          self.f_tt_cdf(before_df[before_df['weekday'].isin([1])]),
                          self.f_tt_cdf(before_df[before_df['weekday'].isin([2])]),
                          self.f_tt_cdf(before_df[before_df['weekday'].isin([3])]),
                          self.f_tt_cdf(before_df[before_df['weekday'].isin([4])]),
                          self.f_tt_cdf(before_df[before_df['weekday'].isin([5])]),
                          self.f_tt_cdf(before_df[before_df['weekday'].isin([6])]),
                          self.f_tt_cdf(after_df[after_df['weekday'].isin([0, 1, 2, 3, 4])]),
                          self.f_tt_cdf(after_df[after_df['weekday'].isin([5, 6])]),
                          self.f_tt_cdf(after_df[after_df['weekday'].isin([0])]),
                          self.f_tt_cdf(after_df[after_df['weekday'].isin([1])]),
                          self.f_tt_cdf(after_df[after_df['weekday'].isin([2])]),
                          self.f_tt_cdf(after_df[after_df['weekday'].isin([3])]),
                          self.f_tt_cdf(after_df[after_df['weekday'].isin([4])]),
                          self.f_tt_cdf(after_df[after_df['weekday'].isin([5])]),
                          self.f_tt_cdf(after_df[after_df['weekday'].isin([6])])
                          ]

        self.plot_dfs4 = [self.f_speed_freq(before_df[before_df['weekday'].isin([0, 1, 2, 3, 4])]),
                          self.f_speed_freq(before_df[before_df['weekday'].isin([5, 6])]),
                          self.f_speed_freq(before_df[before_df['weekday'].isin([0])]),
                          self.f_speed_freq(before_df[before_df['weekday'].isin([1])]),
                          self.f_speed_freq(before_df[before_df['weekday'].isin([2])]),
                          self.f_speed_freq(before_df[before_df['weekday'].isin([3])]),
                          self.f_speed_freq(before_df[before_df['weekday'].isin([4])]),
                          self.f_speed_freq(before_df[before_df['weekday'].isin([5])]),
                          self.f_speed_freq(before_df[before_df['weekday'].isin([6])]),
                          self.f_speed_freq(after_df[after_df['weekday'].isin([0, 1, 2, 3, 4])]),
                          self.f_speed_freq(after_df[after_df['weekday'].isin([5, 6])]),
                          self.f_speed_freq(after_df[after_df['weekday'].isin([0])]),
                          self.f_speed_freq(after_df[after_df['weekday'].isin([1])]),
                          self.f_speed_freq(after_df[after_df['weekday'].isin([2])]),
                          self.f_speed_freq(after_df[after_df['weekday'].isin([3])]),
                          self.f_speed_freq(after_df[after_df['weekday'].isin([4])]),
                          self.f_speed_freq(after_df[after_df['weekday'].isin([5])]),
                          self.f_speed_freq(after_df[after_df['weekday'].isin([6])])
                          ]

    def create_charts(self):
        self.chart11 = MplChart(self, fig_type=self.chart_options.chart_type[0][0], panel=self, region=0, region2=1)
        self.chart21 = MplChart(self, fig_type=self.chart_options.chart_type[1][0], panel=self, region=0, region2=-1)
        self.chart12 = MplChart(self, fig_type=self.chart_options.chart_type[0][1], panel=self, region=0, region2=1)
        self.chart22 = MplChart(self, fig_type=self.chart_options.chart_type[1][1], panel=self, region=0, region2=1)

    def update_figures(self):
        if self.chart11 is not None:
            self.chart11.update_figure()
            self.chart11.draw()
        if self.chart21 is not None:
            self.chart21.update_figure()
            self.chart21.draw()
        if self.chart12 is not None:
            self.chart12.update_figure()
            self.chart12.draw()
        if self.chart22 is not None:
            self.chart22.update_figure()
            self.chart22.draw()

    def update_chart_visibility(self):
        self.chart11.setVisible(True)
        self.chart12.setVisible(self.chart_options.num_cols > 1)
        self.chart21.setVisible(self.chart_options.num_rows > 1)
        self.chart22.setVisible(self.chart_options.num_rows > 1 and self.chart_options.num_cols > 1)

    def add_charts_to_layouts(self):
        # Chart 1
        self.grid_layout.addWidget(self.chart11, 0, 0)
        # Chart 2
        self.grid_layout.addWidget(self.chart12, 0, 1)
        # Chart 3
        self.grid_layout.addWidget(self.chart21, 1, 0)
        # Chart 4
        self.grid_layout.addWidget(self.chart22, 1, 1)

    def options_updated(self):
        self.chart_options = self.project.chart_panel1_opts
        # self.update_plot_data()
        self.update_chart_types()
        self.update_figures()
        self.update_chart_visibility()

    def update_chart_types(self):
        self.chart11.set_fig_type(self.chart_options.chart_type[0][0])
        self.chart12.set_fig_type(self.chart_options.chart_type[0][1])
        self.chart21.set_fig_type(self.chart_options.chart_type[1][0])
        self.chart22.set_fig_type(self.chart_options.chart_type[1][1])

    def connect_radio_buttons(self):
        self.check_wkdy.setChecked(True)
        self.check_wkdy.toggled.connect(lambda: self.toggle_func(0, self.check_wkdy))
        self.check_wknd.toggled.connect(lambda: self.toggle_func(1, self.check_wknd))
        self.check_mon.toggled.connect(lambda: self.toggle_func(2, self.check_mon))
        self.check_tue.toggled.connect(lambda: self.toggle_func(3, self.check_tue))
        self.check_wed.toggled.connect(lambda: self.toggle_func(4, self.check_wed))
        self.check_thu.toggled.connect(lambda: self.toggle_func(5, self.check_thu))
        self.check_fri.toggled.connect(lambda: self.toggle_func(6, self.check_fri))
        self.check_sat.toggled.connect(lambda: self.toggle_func(7, self.check_sat))
        self.check_sun.toggled.connect(lambda: self.toggle_func(8, self.check_sun))

        self.check_wkdy.setEnabled(sum([self.available_days.count(el) for el in range(5)]) > 0)
        self.check_wknd.setEnabled(sum([self.available_days.count(el) for el in range(5, 7)]) > 0)
        self.check_mon.setEnabled(self.available_days.count(0) > 0)
        self.check_tue.setEnabled(self.available_days.count(1) > 0)
        self.check_wed.setEnabled(self.available_days.count(2) > 0)
        self.check_thu.setEnabled(self.available_days.count(3) > 0)
        self.check_fri.setEnabled(self.available_days.count(4) > 0)
        self.check_sat.setEnabled(self.available_days.count(5) > 0)
        self.check_sun.setEnabled(self.available_days.count(6) > 0)

    def connect_combo_boxes(self):
        self.cb_tmc_select.currentIndexChanged.connect(self.tmc_selection_changed)

    def tmc_selection_changed(self):
        if not (self.init_mode or self.no_compute):
            tmc_idx = self.cb_tmc_select.currentIndex()
            self.selected_tmc_name = self.project.get_tmc()['tmc'][tmc_idx]
            self.selected_tmc_len = self.project.get_tmc()['miles'][tmc_idx]
            self.update_figures()

    def connect_check_boxes(self):

        self.check_wkdy.stateChanged.connect(self.check_weekday)
        if sum([self.available_days.count(el) for el in range(5)]) > 0:
            self.check_wkdy.setChecked(True)
        else:
            self.check_wkdy.setDisabled(True)

        self.check_wknd.stateChanged.connect(self.check_weekend)
        if sum([self.available_days.count(el) for el in range(5, 7)]) > 0:
            self.check_wknd.setChecked(True)
        else:
            self.check_wknd.setDisabled(True)

        self.check_mon.stateChanged.connect(self.check_func)
        if self.available_days.count(0) > 0:
            self.check_mon.setChecked(True)
        else:
            self.check_mon.setDisabled(True)

        self.check_tue.stateChanged.connect(self.check_func)
        if self.available_days.count(1) > 0:
            self.check_tue.setChecked(True)
        else:
            self.check_tue.setDisabled(True)

        self.check_wed.stateChanged.connect(self.check_func)
        if self.available_days.count(2) > 0:
            self.check_wed.setChecked(True)
        else:
            self.check_wed.setDisabled(True)

        self.check_thu.stateChanged.connect(self.check_func)
        if self.available_days.count(3) > 0:
            self.check_thu.setChecked(True)
        else:
            self.check_thu.setDisabled(True)

        self.check_fri.stateChanged.connect(self.check_func)
        if self.available_days.count(4) > 0:
            self.check_fri.setChecked(True)
        else:
            self.check_fri.setDisabled(True)

        self.check_sat.stateChanged.connect(self.check_func)
        if self.available_days.count(5) > 0:
            self.check_sat.setChecked(True)
        else:
            self.check_sat.setDisabled(True)

        self.check_sun.stateChanged.connect(self.check_func)
        if self.available_days.count(6) > 0:
            self.check_sun.setChecked(True)
        else:
            self.check_sun.setDisabled(True)

    def check_weekday(self):
        self.no_compute = True
        weekday_checked = self.check_wkdy.isChecked()
        if self.available_days.count(0) > 0:
            self.check_mon.setChecked(weekday_checked)
        if self.available_days.count(1) > 0:
            self.check_tue.setChecked(weekday_checked)
        if self.available_days.count(2) > 0:
            self.check_wed.setChecked(weekday_checked)
        if self.available_days.count(3) > 0:
            self.check_thu.setChecked(weekday_checked)
        if self.available_days.count(4) > 0:
            self.check_fri.setChecked(weekday_checked)
        self.no_compute = False
        self.check_func()

    def check_weekend(self):
        self.no_compute = True
        weekend_checked = self.check_wknd.isChecked()
        if self.available_days.count(5) > 0:
            self.check_sat.setChecked(weekend_checked)
        if self.available_days.count(6) > 0:
            self.check_sun.setChecked(weekend_checked)
        self.no_compute = False
        self.check_func()

    def toggle_func(self, day_select, button):
        if not (self.init_mode or self.no_compute):
            if button.isChecked():
                self.day_select = day_select
                self.update_figures()

    def check_func(self):
        if not (self.init_mode or self.no_compute):
            self.plot_days.clear()
            if self.check_mon.isChecked() is True:
                self.plot_days.append(0)
            if self.check_tue.isChecked() is True:
                self.plot_days.append(1)
            if self.check_wed.isChecked() is True:
                self.plot_days.append(2)
            if self.check_thu.isChecked() is True:
                self.plot_days.append(3)
            if self.check_fri.isChecked() is True:
                self.plot_days.append(4)
            if self.check_sat.isChecked() is True:
                self.plot_days.append(5)
            if self.check_sun.isChecked() is True:
                self.plot_days.append(6)

            if len(self.plot_days) > 0:
                # self.update_plot_data()
                self.update_figures()