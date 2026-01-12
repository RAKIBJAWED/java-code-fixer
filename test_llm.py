from java_code_fixer import JavaCodeFixer
import os

if __name__ == "__main__":
    API_KEY = os.getenv("ANTHROPIC_API_KEY")  # Load from environment variable

    java_code = """
import sun.misc.BASE64Encoder;

public class Main {
    public static void main(String[] args) {
        BASE64Encoder encoder = new BASE64Encoder();
        System.out.println(encoder.encode("hello".getBytes()));
    }
}
"""

    error_message = """
/tmp/java-runner-2f9d2635/Main.java:1: error: cannot find symbol
import sun.misc.BASE64Encoder;
               ^
  symbol:   class BASE64Encoder
  location: package sun.misc
/tmp/java-runner-2f9d2635/Main.java:5: error: cannot find symbol
        BASE64Encoder encoder = new BASE64Encoder();
        ^
  symbol:   class BASE64Encoder
  location: class Main
/tmp/java-runner-2f9d2635/Main.java:5: error: cannot find symbol
        BASE64Encoder encoder = new BASE64Encoder();
                                    ^
  symbol:   class BASE64Encoder
  location: class Main
3 errors
"""

    java_version = "Java 11"

    fixer = JavaCodeFixer(api_key=API_KEY)
    fixed_code = fixer.fix_code(java_code, error_message, java_version)

    print(fixed_code)
