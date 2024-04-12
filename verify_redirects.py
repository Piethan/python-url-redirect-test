import csv
import requests
from termcolor import colored

def verify_redirects(file_path):
    results = []
    with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for line_number, row in enumerate(reader, start=1):
            try:
                source_url = row['source_url'].strip()
                target_url = row['target_url'].strip()
                expected_code = int(row['code'].strip())

                response = requests.get(source_url, allow_redirects=False)
                actual_code = response.status_code
                redirected_to = response.headers.get('Location', None)

                is_correct_code = (actual_code == expected_code)
                is_correct_target = (redirected_to == target_url if redirected_to else False)

                results.append((source_url, target_url, expected_code, actual_code, redirected_to, is_correct_code, is_correct_target, line_number))

            except requests.RequestException as e:
                results.append((source_url, target_url, expected_code, 'Error', 'Error', False, False, line_number))
            except KeyError as e:
                print(colored(f"Missing key in CSV: {e}, Line: {line_number}", 'red'))
                break

    return results

def generate_html_report(results, output_file, title):
    color = 'green' if 'Successful' in title else 'red'
    html_content = f'''
    <html>
    <head>
        <title>{title}</title>
    </head>
    <body>
        <h1>{title}</h1>
        <table border="1" style="width: 100%;">
            <tr>
                <th>Source URL</th>
                <th>Target URL</th>
                <th>Expected Code</th>
                <th>Actual Code</th>
                <th>Redirected To</th>
                <th>Correct Code</th>
                <th>Correct Target</th>
                <th>Line Number</th>
            </tr>
    '''
    for entry in results:
        html_content += f'''
            <tr style="color: {color};">
                <td>{entry[0]}</td>
                <td>{entry[1]}</td>
                <td>{entry[2]}</td>
                <td>{entry[3]}</td>
                <td>{entry[4] or 'None'}</td>
                <td>{'Yes' if entry[5] else 'No'}</td>
                <td>{'Yes' if entry[6] else 'No'}</td>
                <td>{entry[7]}</td>
            </tr>
        '''

    html_content += '''
        </table>
    </body>
    </html>
    '''
    with open(output_file, 'w') as file:
        file.write(html_content)

    print(f"Report generated: {output_file}")

# Main execution
if __name__ == "__main__":
    results = verify_redirects('redirects.csv')
    successes = [res for res in results if res[5] and res[6]]
    errors = [res for res in results if not (res[5] and res[6])]

    generate_html_report(successes, 'results/redirect_verification_success.html', 'URL Redirect Verification Report - Successful')
    generate_html_report(errors, 'results/redirect_verification_error.html', 'URL Redirect Verification Report - Errors')
