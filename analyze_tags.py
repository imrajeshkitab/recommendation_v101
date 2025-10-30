import csv
import json
import ast

def analyze_tags_metadata():
    """Analyze tags_metadata.csv to validate format and count tags."""
    
    csv_file = '/Users/rajesh/Desktop/projects/recommendation_v101/tags_metadata.csv'
    
    all_tags = set()
    row_data = []
    issues = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
            question = row['Question']
            option = row['Option']
            tag_list_str = row['Tag List']
            
            # Check if it's a valid list format
            try:
                # Try to parse as Python literal (handles both JSON and Python list format)
                tag_list = ast.literal_eval(tag_list_str)
                
                if not isinstance(tag_list, list):
                    issues.append(f"Row {idx}: Tag List is not a list - '{tag_list_str}'")
                    tag_list = []
                
                # Check if all elements are strings
                for tag in tag_list:
                    if not isinstance(tag, str):
                        issues.append(f"Row {idx}: Tag '{tag}' is not a string")
                    else:
                        all_tags.add(tag)
                
                row_data.append({
                    'row': idx,
                    'question': question,
                    'option': option,
                    'tag_count': len(tag_list),
                    'tags': tag_list,
                    'valid': True
                })
                
            except (ValueError, SyntaxError) as e:
                issues.append(f"Row {idx}: Invalid format - {str(e)}")
                row_data.append({
                    'row': idx,
                    'question': question,
                    'option': option,
                    'tag_count': 0,
                    'tags': [],
                    'valid': False
                })
    
    # Print Analysis Report
    print("=" * 80)
    print("📊 TAG METADATA ANALYSIS REPORT")
    print("=" * 80)
    
    print(f"\n✅ VALIDATION STATUS")
    print("-" * 80)
    if issues:
        print(f"⚠️  Found {len(issues)} issue(s):\n")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ All Tag List entries are properly formatted!")
    
    print(f"\n📈 STATISTICS")
    print("-" * 80)
    total_rows = len(row_data)
    rows_with_tags = sum(1 for r in row_data if r['tag_count'] > 0)
    rows_without_tags = total_rows - rows_with_tags
    total_tag_instances = sum(r['tag_count'] for r in row_data)
    
    print(f"Total Rows (excl. header):    {total_rows}")
    print(f"Rows with tags:               {rows_with_tags}")
    print(f"Rows without tags:            {rows_without_tags}")
    print(f"Total tag instances:          {total_tag_instances}")
    print(f"Total unique tags:            {len(all_tags)}")
    
    # Show rows without tags
    if rows_without_tags > 0:
        print(f"\n📝 ROWS WITHOUT TAGS:")
        print("-" * 80)
        for r in row_data:
            if r['tag_count'] == 0:
                print(f"   Row {r['row']}: {r['question']} → {r['option']}")
    
    # Tag distribution by question
    print(f"\n📊 TAG DISTRIBUTION BY QUESTION:")
    print("-" * 80)
    question_stats = {}
    for r in row_data:
        q = r['question']
        if q not in question_stats:
            question_stats[q] = {'total_tags': 0, 'options': 0, 'tags': set()}
        question_stats[q]['total_tags'] += r['tag_count']
        question_stats[q]['options'] += 1
        question_stats[q]['tags'].update(r['tags'])
    
    for q, stats in sorted(question_stats.items()):
        avg_tags = stats['total_tags'] / stats['options'] if stats['options'] > 0 else 0
        print(f"\n{q}")
        print(f"   Options: {stats['options']} | Total tags: {stats['total_tags']} | "
              f"Unique tags: {len(stats['tags'])} | Avg per option: {avg_tags:.1f}")
    
    # List all unique tags alphabetically
    print(f"\n📚 ALL UNIQUE TAGS (Alphabetical):")
    print("-" * 80)
    sorted_tags = sorted(all_tags)
    
    # Print in columns for better readability
    tags_per_row = 3
    for i in range(0, len(sorted_tags), tags_per_row):
        row_tags = sorted_tags[i:i+tags_per_row]
        formatted_tags = [f"{j+i+1:3d}. {tag:30s}" for j, tag in enumerate(row_tags)]
        print("   " + "".join(formatted_tags))
    
    print("\n" + "=" * 80)
    
    # Return summary
    return {
        'total_rows': total_rows,
        'total_unique_tags': len(all_tags),
        'total_tag_instances': total_tag_instances,
        'issues': issues,
        'all_tags': sorted_tags
    }


if __name__ == "__main__":
    analyze_tags_metadata()

