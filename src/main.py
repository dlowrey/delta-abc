""" 
Dane Lowrey
Main interface for d-abc features and functionality
"""
from transaction import Transaction

def main():

    # Test transaction
    tnx = Transaction()
    print(tnx.create_output("test", "rec", 50))

if __name__ == "__main__":
    main()
