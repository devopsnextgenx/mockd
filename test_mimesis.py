#!/usr/bin/env python3
"""
Simple MockNode test
"""

import sys
import os

# Test if we can import mimesis
try:
    from mimesis import Generic, Person, Text, Numeric
    print("✓ Mimesis import successful")
    
    # Test basic functionality
    generic = Generic()
    person = Person()
    text = Text()
    numeric = Numeric()
    
    print(f"✓ Sample person name: {person.full_name()}")
    print(f"✓ Sample email: {person.email()}")
    print(f"✓ Sample text: {text.word()}")
    print(f"✓ Sample number: {numeric.integer_number(1, 100)}")
    print(f"✓ Sample UUID: {str(generic.uuid())}")
    
    print("\n🎉 Mimesis is working correctly!")
    
except ImportError as e:
    print(f"❌ Failed to import mimesis: {e}")
    
    # Try manual installation
    print("Attempting to install mimesis...")
    import subprocess
    import sys
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'mimesis==4.1.3'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Mimesis installed successfully")
            # Try import again
            from mimesis import Generic
            print("✓ Import successful after installation")
        else:
            print(f"❌ Installation failed: {result.stderr}")
    except Exception as install_error:
        print(f"❌ Installation error: {install_error}")

except Exception as e:
    print(f"❌ Unexpected error: {e}")
