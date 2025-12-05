import tkinter as tk

# Function to add the two numbers and show the result
def add_numbers():
    try:
        num1 = float(entry_num1.get())
        num2 = float(entry_num2.get())
        result = num1 + num2
        label_result.config(text=f"Result: {result}")
    except ValueError:
        label_result.config(text="Please enter valid numbers")

# Create the main window
root = tk.Tk()
root.title("Simple Adder")

# Create labels for the two numbers
label_num1 = tk.Label(root, text="Enter first number:")
label_num1.grid(row=0, column=0, padx=10, pady=5)

label_num2 = tk.Label(root, text="Enter second number:")
label_num2.grid(row=1, column=0, padx=10, pady=5)

# Create entry widgets for number inputs
entry_num1 = tk.Entry(root)
entry_num1.grid(row=0, column=1, padx=10, pady=5)

entry_num2 = tk.Entry(root)
entry_num2.grid(row=1, column=1, padx=10, pady=5)

# Create a button to trigger the addition
button_add = tk.Button(root, text="Add", command=add_numbers)
button_add.grid(row=2, columnspan=2, pady=10)

# Label to display the result
label_result = tk.Label(root, text="Result: ")
label_result.grid(row=3, columnspan=2, pady=10)

# Start the Tkinter main loop
root.mainloop()

    