def main():
    notes_count = 1
    notes_approved = 0
    notes_reproved = 0
    average_approved = 0
    average_reproved = 0
    average_total = 0
    notes_total_number = int(input("Enter the total number of notes: "))

    while notes_count <= notes_total_number:
        actual_note = int(input(f"Enter note number {notes_count}:"))
        if actual_note >= 70:
            notes_approved += 1
            average_approved += actual_note
        else:
            notes_reproved += 1
            average_reproved += actual_note
        average_total += actual_note / notes_total_number
        notes_count += 1

    if notes_approved > 0:
        average_approved = average_approved / notes_approved
    else:
        average_approved = 0

    if notes_reproved > 0:
        average_reproved = average_reproved / notes_reproved
    else:
        average_reproved = 0

    print(f"Approved notes: {notes_approved}")
    print(f"Average of approved notes: {average_approved}")
    print(f"Reproved notes: {notes_reproved}")
    print(f"Average of reproved notes: {average_reproved}")
    print(f"Average of all notes: {average_total}")
    

if __name__ == "__main__":
    main()