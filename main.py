
import random
import time
from math import *
import multiprocessing
import tkinter
from tkinter import *
from tkinter import messagebox

Amount_of_Population = 25
Len_Population = 300
Number_of_generations = 20
Percentage_of_tops = 15

class Global_Time:
    Time=time.time()
def Correct_Individ(function, individ):
    try:
        test_value = int(Function_Value(function, individ))
        return True
    except:
        return False

def Function_Value(function, individ):
    try:
        x1 = individ[0]
        x2 = individ[1]
        x3 = individ[2]
        x4 = individ[3]
        x5 = individ[4]
        x6 = individ[5]
        x7 = individ[6]
        x8 = individ[7]
        x9 = individ[8]
    except:
        pass
    FV = eval(function)
    return FV

def crossing(parent1, parent2, function):
    child = []
    FV = min(Function_Value(function, parent1), Function_Value(function, parent2))
    for j in range(3):
        child.clear()
        for i in range(len(parent1)):
            child.append(random.uniform(parent1[i], parent2[i]))
        try:
            if (Function_Value(function, child) < FV):
                return child
        except:
            pass
    if (Function_Value(function, parent1) < Function_Value(function, parent2)):
        return parent1
    return parent2

def Generate_a_population(function, number_of_variables, segments):
    population = []
    individ = []

    for i in range(number_of_variables):
        individ.append(segments[i][0])
    if (Correct_Individ(function, individ)):
        population.append(individ.copy())
    individ.clear()
    # 2 особых индивида, на границах отрезков
    for i in range(number_of_variables):
        individ.append(segments[i][1])
    if (Correct_Individ(function, individ)):
        population.append(individ.copy())
    individ.clear()

    if (time.time()-Global_Time.Time>30):
        messagebox.showinfo('Превышено время работы', "К сожалению, найти min, max не удалось")
        return 0

    while (len(population) < Len_Population):
        individ = []
        for i in range(number_of_variables):
            individ.append(random.uniform(segments[i][0], segments[i][1]))
        if (Correct_Individ(function, individ)):
            population.append(individ.copy())

        if (time.time() - Global_Time.Time > 30):
            messagebox.showinfo('Превышено время работы', "К сожалению, найти min, max не удалось")
            return 0

        individ.clear()
    return population


def Generate_a_new_population(population, function, number_of_variables, segments):
    New_Population = []
    amount_top = Len_Population * Percentage_of_tops // 100
    while (len(New_Population) < (Len_Population)):
        parent1 = population[random.randint(0, amount_top - 1)]
        parent2 = population[random.randint(0, amount_top - 1)]
        child = crossing(parent1, parent2, function)
        try:
            test_variable = Function_Value(function, child)
            New_Population.append(child)
        except:
            pass
    return New_Population

def Natural_Selection(population, function, number_of_variables, segments, queue):

    if (time.time()-Global_Time.Time>30):
        messagebox.showinfo('Превышено время работы', "К сожалению, найти min, max не удалось")
        return 0

    def sort_key(individ):
        return Function_Value(function, individ)

    local_population = population.copy()
    for i in range(Number_of_generations):
        new_population = Generate_a_new_population(local_population, function, number_of_variables, segments)
        new_population.sort(key=sort_key)
        local_population = []
        amount_tops = Percentage_of_tops * Len_Population // 100
        for j in range(amount_tops):
            local_population.append(new_population[j])
        while (len(local_population) < Len_Population):
            index = random.randint(amount_tops - 1, len(new_population) - 1)
            local_population.append(new_population[index])
        new_population.clear()

    top_individ = local_population[0]
    FV = Function_Value(function, local_population[0])
    for i in range(1, Len_Population):
        Buf_FV = Function_Value(function, local_population[i])
        if (Buf_FV < FV):
            FV = Buf_FV
            top_individ = local_population[i]
    queue.put(top_individ)



if (__name__=="__main__"):

    def Find_Minim_Function(function, number_of_variables, segments):
        if (time.time() - Global_Time.Time > 30):
            messagebox.showinfo('Превышено время работы', "К сожалению, найти min, max не удалось")
            return 0
        Populations = []  # лист, состоящицй из популяций
        Top_Individs = []  # лист, состоящий из лучших индивидов (для каждой популяции находим лучшего индивида) и значения функции Top_Individs[i] = [значение функции, individ]

        for i in range(Amount_of_Population):
            population = Generate_a_population(function, number_of_variables, segments)  # делается и так быстро, распараллеливание ускорит незначительно
            Populations.append(population.copy())
        queue = multiprocessing.Queue()  # специальная очередь, чтобы положить в нее результат работы процесса
        arr_process = []


        for population in Populations:  # а вот это уже можно распараллелить. Что-то не так с if __name__==main
            arr_process.append(multiprocessing.Process(target=Natural_Selection, args=(
            population, function, number_of_variables, segments, queue)))
            arr_process[-1].start()

        for process in arr_process:
            process.join()
        while (queue.qsize() > 0):
            top_individ = queue.get()
            Top_Individs.append([Function_Value(function, top_individ), top_individ.copy()])

        Top_Individs.sort()
        Top_individ = Top_Individs[0]
        if (Top_individ != None):
            return Top_individ

    def Find_Maxim_Function(function, number_of_variables, segments):
        func = "-(" + function + ")"
        individ = Find_Minim_Function(func, number_of_variables, segments)[1]
        FV = Function_Value(function, individ)
        return [FV, individ]

    def CreateVarElemets(LblVar, txtEdit, Count, CurVarBegin):  # Создадим Count элементов типа label +Spinbox для задания ООФ переменных
        #  CurVarBegin - кол-во элементов по умолчанию (в начале -1)
        #  Count - мксимальное кол-во элементов
        txt = "Отрезок для переменной  x"
        py = 5  # padx Или pady - это отступы
        px = 0
        wd = 12  # ширина текстового поля

        for i in range(1, Count + 1):
            LblVar[i] = Label(window, text=txt + str(i) + ":", font=('TkTextFont 14'))
            LblVar[i].grid(column=0, row=i, padx=10, pady=py)  # padx Или pady - это отступы

            txtEdit[i] = Entry(window, width=wd, font=('TkTextFont 14'))
            txtEdit[i].insert(0, " 0;1 ")
            txtEdit[i].grid(column=1, row=i, padx=px)

        #  Сделаем "лишние "элементы невидимыми
        for i in range(Count, CurVarBegin - 1, -1):
            if i < Count:
                LblVar[i].grid(column=0, row=i, pady=py)  # Сделали видимым
                txtEdit[i].grid(column=1, row=i, padx=px)

                LblVar[i + 1].grid_forget()  # Сделали не видимым
                txtEdit[i + 1].grid_forget()
            else:
                LblVar[i].grid(column=0, row=i, pady=py)  # Сделали видимым
                txtEdit[i].grid(column=1, row=i, padx=px)


    def ClickedSpin(LblVar, txtEdit, CountV):
        # children = window.winfo_children(VarCount)
        py = 5  # padx Или pady - это отступы
        px = 3

        SpinCount = int(spin.get())
        CountVarMax = CountV
        for i in range(CountVarMax, SpinCount - 1, -1):
            if i < CountVarMax:
                LblVar[i].grid(column=0, row=i, pady=py)  # Сделали видимым
                txtEdit[i].grid(column=1, row=i, padx=px)

                LblVar[i + 1].grid_forget()  # Сделали не видимым
                txtEdit[i + 1].grid_forget()
            else:
                LblVar[i].grid(column=0, row=i, pady=py)  # Сделали видимым
                txtEdit[i].grid(column=1, row=i, padx=px)


    def ClickedMax(txtEdit):
        # CountVar = CountV
        CountVar = int(spin.get())
        segments = []
        for i in range(1, CountVar + 1):
            stroka = txtEdit[i].get()
            segm=str_to_segment(stroka)
            if (segm=="Krivoy"):
                messagebox.showinfo('Ошибка в значении oтрезка ', stroka)
                return 0

            segments.append(segm)

        txtFunct = txtFunction.get()

        Global_Time.Time = time.time()  # старт работы счетчика времени

        if Function_Validation(CountVar,segments,txtFunct) == 0:

            Max = Find_Maxim_Function(txtFunct, CountVar, segments)
            for _ in range(len(Max[1])):
                Max[1][_] = round(Max[1][_], 5)
            txt = "Max = " + str(round(Max[0], 5)) + " , в точке  " + str(Max[1])
            messagebox.showinfo('Максимум функции', txt)

    def ClickedMin(txtEdit):
        CountVar = int(spin.get())
        segments = []
        for i in range(1, CountVar + 1):
            stroka = txtEdit[i].get()
            segm = str_to_segment(stroka)
            if (segm == "Krivoy"):
                messagebox.showinfo('Ошибка в значении oтрезка ', stroka)
                return 0
            segments.append(str_to_segment(stroka))

        txtFunct = txtFunction.get()

        Global_Time.Time=time.time()   # старт работы счетчика времени

        if Function_Validation(CountVar, segments, txtFunct) == 0:
            Min = Find_Minim_Function(txtFunct, CountVar, segments)
            for _ in range(len(Min[1])):
                Min[1][_] = round(Min[1][_], 5)
            txt = "Min = " + str(round(Min[0], 5)) + " , в точке  " + str(Min[1])
            messagebox.showinfo('Минимум функции', txt)

    def str_to_segment(s):
        try:
            a = ""
            b = ""
            flag = 0
            for elem in s:
                if (elem == ';' or elem==','):
                    flag = 1
                    continue
                if (flag == 0):
                    a += elem
                else:
                    b += elem
            a = float(a)
            b = float(b)
            return [a, b]
        except:
            return "Krivoy"

    window = Tk()
    window.title(" ВЫЧИСЛЕНИЕ  МАКСИМУМА  И  МИНИМУМА  ФУНКЦИИ (MULTIPROCESSING )")
    window.geometry('1000x500')

    CountVarmax = 9  # Максимальное количество переменных
    CurVarBegin = 1  # По умолчанию количество переменных

    class Global:
        LblVar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        txtEdit = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


    #  Определим лейблу количества переменных функции в 1-й колонке и 1-й строке

    lblVarCount = Label(window, text="Количество переменных      :", font=('TkTextFont 14'))
    lblVarCount.grid(column=0, row=0, pady=40)

    #  Определим элемент типа Spinbox для задания количества переменных

    spin = Spinbox(window, from_=1, to=9, width=3, font=('TkTextFont 14'), textvariable=str(CurVarBegin),
                   command=lambda: ClickedSpin(Global.LblVar, Global.txtEdit, CountVarmax))
    spin.grid(column=1, row=0, sticky='w', pady=5)

    #  Определим массивы элементов типа label и Entry кол-вом CountVarMax для задания ООФ переменных
    CreateVarElemets(Global.LblVar, Global.txtEdit, CountVarmax, CurVarBegin)

    #  Определим label и Entry для выражения функции

    lblFuction = Label(window, text="Задайте выражение функции : ", font=('TkTextFont 14'))
    lblFuction.grid(column=2, row=0, sticky='w', padx=15)
    txtFunction = Entry(window, width=45, font=('TkTextFont 14'))
    txtFunction.insert(0, " x1*x2+x3-x4*x5/x2 ")
    txtFunction.grid(column=2, row=1, padx=15)

    #  Определим label и button для вычисления максимума функции

    calcmaxbutton = Button(window, text="Найти max: ", font=('TkTextFont 14'), command=lambda: ClickedMax(Global.txtEdit))
    calcmaxbutton.grid(column=2, row=2, sticky='w', padx=15)

    lblMax = Label(window, text="", font=('TkTextFont 14'))
    lblMax.grid(column=2, row=3, sticky='w', padx=15)

    #  Определим label и button для вычисления минимума функции

    calcminbutton = Button(window, text="Найти min: ", font=('TkTextFont 14'), command=lambda: ClickedMin(Global.txtEdit))
    calcminbutton.grid(column=2, row=4, sticky='w', padx=15)
    lblMin = Label(window, text="", font=('TkTextFont 14'))
    lblMin.grid(column=2, row=5, sticky='w', padx=15)

    def mess_error():
        messagebox.showinfo('Заголовок', 'Текст')

    def ValidateFunctionExpression(CountVar, segments, txtFunct):
        flag=0
        try:
            x1 = float(segments[0][0])  # левая граница первого отрезка
            if CountVar > 1:
                x2 = float(segments[1][0])  # левая граница второго отрезка
            FV = eval(txtFunct)
        except:
            flag=1
            messagebox.showinfo('Ошибка при вычислении значения функции ', "Некорректный ввод данных")

        try:
            x1 = float(segments[0][1])  # правая граница первого отрезка

            if CountVar > 1:
                x2 = float(segments[1][1])  # правая граница второго отрезка

            FV = eval(txtFunct)
        except:
            flag = 1
            messagebox.showinfo('Ошибка при вычислении значения функции ', "Некорректный ввод данных")

        return flag

    def Function_Validation(CountVar, segments, txtFunct):
        flag = 0
        try:
            x1 = segments[0][0]
            x2 = segments[1][0]
            x3 = segments[2][0]
            x4 = segments[3][0]
            x5 = segments[4][0]
            x6 = segments[5][0]
            x7 = segments[6][0]
            x8 = segments[7][0]
            x9 = segments[8][0]
        except:
            pass

        try:
            try:
                eval(txtFunct)
                flag=1
            except ValueError:
                flag = 1
        except:
            pass

        try:
            try:
                eval(txtFunct)
            except ArithmeticError:
                flag = 1
        except:
            pass

        if (flag == 0):
            messagebox.showinfo('Ошибка при вычислении значения функции ', "Некорректный ввод данных")
            return "Krivoy"
        return 0

    window.mainloop()















