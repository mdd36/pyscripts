import pandas as pd
import os, sys

# Constants
categories = ["How was this student's commitment to the team objectives?",
              "How well does this student value others' time?",
              "How well does this student make contributions in team meetings?",
              "Does this student help make effective design decisions?",
              "How was this student's attitude towards the team?",
              "Assign an overall rating to this student",
              "Any comment you want to add to your rating?",
              "What is the best feature of this student as a team mate?",
              "What constructive feedback can you give this student about their role on the team?"]
header = "NetID of student being evaluated"
correct_usage = """
            Error in usage: Should be
            python /path/to/pareser.py project netid1 <netid2, netid3, ...>
            Where project is the name of the .xlsx file, with or without extension
            """
underline = "=============================================================================================\n"
v_padding = "\n\n\n"
box_width = 20
sheet_name = "Form Responses 1"
err_msg = "***Could not find the NetID(s) {} in the file***"
out_type = ".txt"
top_bottom_box = "**********************\n"
middle_box = "*{}*\n"


def main():
    check_args()
    project, names = parse_args()
    df = load_spreadsheet(project)
    out = parse(df, names)
    s = build_output_string(names, out)
    write_file(project, s)


def parse(df, names):
    print("Parsing for net ids...")
    out = dict()
    seen = {name: 0 for name in names}
    suffix = 0
    while suffix != -1:
        suffix = find_in_categories(df, names, out, seen, suffix)
    unfound = [name for name in seen if seen[name] == 0]
    if unfound:
        err_print(err_msg.format(unfound))
        for name in unfound:
            out.pop(name)
            names.remove(name)
    print("Done")
    return out


def find_in_categories(df, names, out, seen, suffix_int):
    suffix = ("."+str(suffix_int) if suffix_int else "")
    status = 0
    for name in names:
        status = find_names(df, name, out, seen, suffix)
    return -1 if status else suffix_int + 1


def find_names(df, name, out, seen, suffix):
    header_ = header + suffix
    try:
        row = df.loc[df[header_] == name]
    except KeyError:
        return 1
    sb = out[name] if name in out else dict()
    for category in categories:
        add_response(category, name, out, row, sb, seen, suffix)
    return 0


def add_response(category, name, out, row, sb, seen, suffix):
    category_ = category + suffix
    s = "\n".join(map(str, row[category_].tolist()))
    list_ = sb[category] if category in sb else list()
    if s != "":
        list_.append(s + "\n")
        seen[name] += 1
    sb[category] = list_
    out[name] = sb


def parse_args():
    names = list()
    project = os.path.splitext(str(sys.argv[1]))[0]
    for i in range(2, len(sys.argv)):
        names.append(sys.argv[i])
    return project, names


def check_args():
    if len(sys.argv) < 3:
        err_print(correct_usage)
        sys.exit(1)


def load_spreadsheet(project):
    print("Loading file...")
    x1 = pd.ExcelFile(os.path.join(os.getcwd(), project + ".xlsx"))
    df = x1.parse(sheet_name)
    print("Done")
    return df


def write_file(project, s):
    print("Writing file...")
    with open(os.path.join(os.getcwd(), project + out_type), 'w+') as file:
        file.write(s)
    print("Done")


def build_output_string(names, out):
    sb = list()
    print("Building output...")
    for name in names:
        sb.append(build_header(name))
        eval_ = out[name]
        for category in eval_.keys():
            add_feedback(category, eval_, sb)
    print("Done")
    return ''.join(sb)


def add_feedback(category, eval_, sb):
    sb.append(category + "\n")
    sb.append(underline)
    sb.append("\n".join(eval_[category]))
    sb.append(v_padding)


def build_header(name):
    middle = middle_box.format(name.center(box_width, " "))
    return top_bottom_box + middle + top_bottom_box + "\n"


def err_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    main()
