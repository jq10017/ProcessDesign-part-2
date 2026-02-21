def main():                                                                #Jalin Quick
    num_str = input("Enter a decimal number: ")
    format_choice = input("Choose the format to convert to (bin, dec, hex): ").lower()
    
    try:
        num = int(num_str, 10)
    except ValueError:
        num = None
    
    overflow = 0
    saturated = 0
    
    if num is None:
        print("Invalid input. Please enter a valid decimal number.")
    elif num < -2147483648:
        num = -2147483648
        overflow = 1
        saturated = 1
        print(f"The number you entered is outside of the boundary so your number is saturated to: {num}")
        print(f"Overflow Flag: {overflow}/1")
        print(f"Saturated Flag: {saturated}/1")
    elif num > 2147483647:
        num = 2147483647
        overflow = 1
        saturated = 1
        print(f"The number you entered is outside of the boundary so your number is saturated to: {num}")    
        print(f"Overflow Flag: {overflow}/1")
        print(f"Saturated Flag: {saturated}/1")
    else:
        if format_choice == "bin":
            converted = bin(num)
        elif format_choice == "hex":
            converted = hex(num)
        else:
            converted = str(num)
        
        print(f"The format you chose  was {format_choice} and the number you entered converted is: {converted}")
        print(f"Overflow Flag: {overflow}/1")
        print(f"Saturated Flag: {saturated}/1")

if __name__ == "__main__":
    main()