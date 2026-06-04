# A variable storea a value
student_name = "vaibhavi"
marks = 45
is_passed = True

print(student_name)
print(marks)
print(is_passed)

if marks >= 75:
    print(student_name + " has passed the exam.")
elif marks >= 50:
    print(student_name + " has passed the exam with a low score.")
elif marks >= 35:
    print(student_name + " has passed the exam with a very low score.")   
else:
    print(student_name + " has failed the exam.")



'''@app.router('/')
def home():
    return render_template('base.html')

@app.router('/')
def home():
    return render_template('student.html')'''

#student = [
   # {"name": tanuja,"Roll_no": 12,"marks": 85},
    #{"name": tanuja,"Roll_no": 12,"marks": 85},
    #{"name": tanuja,"Roll_no": 12,"marks": 85},
    #{"name": dnyaneshwari,"Roll_no": 12,"marks": 85},
#]