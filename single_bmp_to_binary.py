from library_bmp_to_binary import bmp_to_binary



def main():
    print("Welcome to the Converter. Put your BMP FIle in this folder.")
    file_name = input("Whats the name of your bmp file?('yourfile.bmp')")
    bin_name = input("What should be the output name of the bin File?('yourfile.bin')")

    # Converts BPMs into binary Data
    bmp_to_binary(file_name, bin_name)

    # Print Done
    print("\n")
    print('You can find the Binary Code at the workspace')
    print("\n")
    print("The Job is Done. Thank you for using the converter.")
    print("Credits: ")
    print("Phil Meyer, 2020")

if __name__ == "__main__":
    main()