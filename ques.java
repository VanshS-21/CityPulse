
class CustomStringJoiner {
    String delimiter;
    String prefix;
    String suffix;

    public CustomStringJoiner(String delimiter, String prefix, String suffix) {
        this.delimiter = delimiter;
        this.prefix = prefix;
        this.suffix = suffix;
        this.elements = new ArrayList<>();
    }

    public void add(String element) {
        elements.add(element);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(prefix);
        for (int i = 0; i < elements.size(); i++) {
            sb.append(elements.get(i));
            if (i < elements.size() - 1) {
                sb.append(delimiter);
            }
        }
        sb.append(suffix);
        return sb.toString();
    }
}

class Main {
    public static void main(String[] args) {
        CustomStringJoiner sj = new CustomStringJoiner(",", "[", "]");
        sj.add("C");
        sj.add("C++");
        sj.add("Java");
        System.out.println(sj);
    }
}