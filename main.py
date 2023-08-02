import tkinter
from tkinter.ttk import Frame, Label, Scale, Style, Button, OptionMenu, Entry
import matplotlib.pyplot as plt
import requests
import time
import datetime as dt
import math


class ScaleBar(Frame):
    def __init__(self):
        super().__init__()
        self.trade_time = []
        self.graph = []
        self.graph_type = 2
        self.mov_avg = []
        self.initUI()

        self.candles_low = []
        self.candles_high = []
        self.candles_open = []
        self.candles_close = []

    def initUI(self):
        self.master.title("Шкала с ползунком")
        self.style = Style()
        self.style.theme_use("default")
        self.pack()

        label = Label(text='Значение параметра k')
        scale = Scale(self, from_=0, to=1, command=self.onScale)
        btn_collect_data = Button(text='Собрать данные', command=self.collect_data)

        self.options_graph = [
            "Выберите тип графика",
            "Цена открытия",
            "Самая низкая цена",
            "Цена закрытия",
            "Объём продаж",
            'Свечи',
        ]

        self.variable_graph = tkinter.StringVar()
        self.variable_graph.set(self.options_graph[0])
        drop_graph = OptionMenu(root, self.variable_graph, *self.options_graph, command=self.getvariable)

        lbl1 = Label(text='Валютная пара ')
        self.entr1 = Entry()
        lbl2 = Label(text='Кол-во свечей ')
        self.entr2 = Entry()
        self.btn_levels = Button(text='Нарисовать уровни', command=self.draw_level)
        self.btn_levels.pack()

        self.options_frame = [
            "Выберите тип фрейма",
            "1",
            "3",
            "5",
            "15",
            '30',
            '60',
            '120',
            '240',
            '360',
            '720',
            'D',
            'M',
            'W'
        ]

        self.variable_frame = tkinter.StringVar()
        self.variable_frame.set(self.options_graph[0])
        drop_frame = OptionMenu(root, self.variable_frame, *self.options_frame, command=self.getframe)

        scale.pack(side=tkinter.LEFT, padx=15)
        label.pack()
        drop_graph.pack()
        btn_collect_data.pack()
        self.var = tkinter.IntVar()
        self.label = Label(self, text=0, textvariable=self.var)
        self.label.pack(side=tkinter.LEFT)

        lbl1.pack()
        self.entr1.pack()
        lbl2.pack()
        self.entr2.pack()
        drop_frame.pack()

    def draw_level(self):
        z = 70 #число свечей в сегменте
        koeff = 0.005 #диапазон, в котором сходимость будет
        #подбирать автоматически коэффицент в зависимости от валюты
        min_price_arr = []
        max_price_arr = []
        min_price_indx_arr = []
        max_price_indx_arr = []

        iter = self.kline % z
        for k in range(iter):
            start_point = k*z
            if self.kline - k*z < z:
                end_point = self.kline-1
            else:
                end_point = (k+1)*z
            if start_point > end_point:
                break
            time_start_point = self.trade_time[start_point]
            time_end_point = self.trade_time[end_point]
            min = self.candles_low[start_point]
            max = self.candles_high[start_point]
            for i in range(start_point, end_point): #подумать над более эффективным алгоритмом определения лок.макс. и лок.мин
                # добавить цены
                if self.candles_low[i] < self.candles_low[i+1] and self.candles_low[i-1] > self.candles_low[i]:
                    min_price_arr.append(self.candles_low[i])
                    min_price_indx_arr.append(i)
                    plt.plot(self.trade_time[i], self.candles_low[i], 'r*')
                if self.candles_high[i] > self.candles_high[i+1] and self.candles_high[i] > self.candles_high[i-1]:
                    max_price_arr.append(self.candles_high[i])
                    max_price_indx_arr.append(i)
                    plt.plot(self.trade_time[i], self.candles_high[i], 'g*')

                if self.candles_high[i] > max:
                    max = self.candles_high[i]
                if self.candles_low[i] < min:
                    min = self.candles_low[i]

            plt.hlines(min, time_start_point, time_end_point, colors='r')
            plt.hlines(max, time_start_point, time_end_point, colors='g')
            i = 0
            dict_max = {}
            for t in max_price_arr:
                for k in max_price_arr:
                    if ((koeff+1)*t>=k and (1-koeff)*t<=k) and t != k:
                        i += 1
                if i >= 2:
                    plt.hlines(t, time_start_point, time_end_point, colors='g')
                    dict_max.update({t: [i, time_start_point, time_end_point]})
                i = 0

            dict_min = {}
            for t in min_price_arr:
                for k in min_price_arr:
                    if ((koeff+1)*t>=k and (1-koeff)*t<=k) and t != k:
                        i += 1
                if i >= 2:
                    dict_min.update({t: [i, time_start_point, time_end_point]})
                    plt.hlines(t, time_start_point, time_end_point, colors='r')
                i = 0
            max_price_arr = []
            min_price_arr = []
            plt.show()

        print(dict_max)
        print(dict_min)

    def getvariable(self, value):
        if value == self.options_graph[1]:
            self.graph_type = 2
        elif value == self.options_graph[2]:
            self.graph_type = 3
        elif value == self.options_graph[3]:
            self.graph_type = 4
        elif value == self.options_graph[4]:
            self.graph_type = 5
        elif value == self.options_graph[5]:
            self.graph_type = 6

    def getframe(self, value):
        for i in self.options_frame:
            if value == i:
                self.variable_frame = i
                break

    def collect_data(self):

        self.trade_time = []
        self.graph = []

        self.interval_time_type = self.variable_frame # режим времени/свечек
        self.kline = int(self.entr2.get())  # кол-во свечек для отображения

        times = math.ceil(self.kline / 200)
        interval = 200
        end_ds = int(time.time() * 1000)

        # 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, M, W
        if self.interval_time_type == 'W':
            start_ds = end_ds - 86400000 * (self.kline * 365)
        elif self.interval_time_type == 'M':
            start_ds = end_ds - 86400000 * (self.kline * 30)
        elif self.interval_time_type == 'D':
            start_ds = end_ds - 86400000 * self.kline
        else:
            start_ds = end_ds - 60000 * int(self.interval_time_type) * self.kline
        result = []
        start = 0
        end = 0
        for i in range(times):
            if i + 1 == times:
                interval = self.kline % 200
            if i == 0:
                if self.interval_time_type == 'W':
                    start = start_ds
                    end = start_ds + 86400000 * (interval * 365)
                elif self.interval_time_type == 'M':
                    end = start_ds + 86400000 * (interval * 30)
                elif self.interval_time_type == 'D':
                    start = start_ds
                    end = start_ds + 86400000 * interval
                else:
                    start = start_ds
                    end = start_ds + 60000 * int(self.interval_time_type) * interval
            else:
                start = end
                if self.interval_time_type == 'W':
                    end = start + 86400000 * (interval * 365)
                elif self.interval_time_type == 'M':
                    end = start + 86400000 * (interval * 30)
                elif self.interval_time_type == 'D':
                    end = start + 86400000 * interval
                else:
                    end = start + 60000 * int(self.interval_time_type) * interval

            url = 'https://api.bybit.com'
            path = '/v5/market/kline'
            URL = url + path

            params = {
                'category': 'inverse',
                'symbol': self.entr1.get(),
                'interval': self.interval_time_type,
                'start': start,
                'end': end,
            }
            time.sleep(0.2)
            f = requests.get(URL, params=params).json().get('result').get('list')
            for i in reversed(f):
                T = dt.datetime.fromtimestamp(float(i[0]) / 1000.0)
                new_list = []
                new_list.append(T)
                new_list.append(i[1])
                new_list.append(i[2])
                new_list.append(i[3])
                new_list.append(i[4])
                new_list.append(i[5])
                new_list.append(i[6])
                result.append(new_list)

        if self.graph_type != 6:
            for i in range(len(result)):
                self.trade_time.append(result[i][0])
                self.graph.append(float(result[i][self.graph_type]))
        else:
            for i in range(len(result)):
                self.trade_time.append(result[i][0])
                self.candles_open.append(float(result[i][1]))
                self.candles_high.append(float(result[i][2]))
                self.candles_low.append(float(result[i][3]))
                self.candles_close.append(float(result[i][4]))
        print(result)

    def build_plot(self, val):

        if self.graph_type != 6:
            res = self.graph[0]
            self.mov_avg = []
            i = 0
            while i < len(self.graph):
                res = float(self.graph[i]) * float(val) + res * (1 - float(val))
                self.mov_avg.append(res)
                i += 1

            plt.figure('График')
            plt.clf()
            plt.title('красный - оригинальный, синий - аппроксимированный')
            plt.plot(self.trade_time, self.mov_avg, color="blue")
            plt.plot(self.trade_time, self.graph, color="red")
            plt.show()
        else:
            plt.figure('График')
            plt.clf()
            plt.title('Зеленый - рост, красный - падение')

            for i in range(len(self.trade_time)):

                print('========================')
                print(i)
                if self.candles_close[i] - self.candles_open[i] >= 0:

                    print('rise')
                    color = 'green'
                    height = self.candles_close[i] - self.candles_open[i]
                    bottom = self.candles_open[i]
                else:
                    print('fall')
                    color = 'red'
                    height = self.candles_open[i] - self.candles_close[i]
                    bottom = self.candles_close[i]

                print(self.trade_time[i], self.candles_open[i], self.candles_close[i], self.candles_low[i], self.candles_high[i])
                print('========================')

                plt.vlines(self.trade_time[i], self.candles_low[i], self.candles_high[i], color=color)
                plt.bar(self.trade_time[i], height, 0.001, bottom, color=color)
            plt.grid()
            plt.show()

    def onScale(self, val):
        v = round(float(val), 3)
        self.var.set(v)
        self.build_plot(val)


if __name__ == '__main__':
    root = tkinter.Tk()
    scale_bar = ScaleBar()
    root.mainloop()