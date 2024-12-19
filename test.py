starting_amount = 5000
savings = 0
current_balence = starting_amount
for i in range(12):
    print(f"month {i + 1}")
    savings += 4000
    current_balence += (current_balence) * (0.022 * (30.437)) - 4000
    print(f"Current Balance: {current_balence}")
    print(f"Salary:          {savings}")

    