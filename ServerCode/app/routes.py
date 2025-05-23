from flask import render_template,  request, redirect, flash
from app import app
from app.models import User, Question, db, Submission
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import current_user
Q
@app.route('/')
@app.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")


def UploadPage():
        return render_template("UploadPage.html")
    

@app.route('/SearchPage')
def SearchPage():
    return render_template("SearchPage.html")

@app.route('/UserPage')
@login_required
def UserPage():
    return render_template("UserPage.html", current_user=current_user)

@app.route('/QuestionDescription')
def QuestionDescriptionPage():
    question_id = request.args.get('id', type=int)
    if question_id is None:
        abort(400, description="Missing question ID.")
    question = Question.query.get_or_404(question_id)
    return render_template("QuestionDescription.html", question=question)

@app.route('/QuestionStat')
def QuestionStatPage():
    question_id = request.args.get('id', type=int)
    
    # Fetch the most recent submission for the current user and question
    submission = Submission.query.filter_by(
        user_id=current_user.id,
        question_id=question_id
    ).order_by(Submission.timestamp.desc()).first()
    
    # Prepare user score data
    if submission:
        user_score = {
            'time_taken': submission.runtime_sec,
            'tests_ran': submission.tests_run,
            'code_length': submission.lines_of_code,
            'passed': submission.passed
        }
    else:
        user_score = {
            'time_taken': "N/A",
            'tests_ran': "N/A",
            'code_length': "N/A",
            'passed': "N/A"
        }

    # Fetch the question
    question = Question.query.get_or_404(question_id)

    # Get all submission times for this question
    submission_times = [s.runtime_sec for s in question.submissions]
    if not submission_times:
        submission_times = [0]

    # Generate dynamic bins for the histogram
    min_time = min(submission_times)
    max_time = max(submission_times)
    bin_count = 10
    bin_size = max(1, (max_time - min_time) // bin_count + 1)
    bins = list(range(min_time, max_time + bin_size, bin_size))

    # Calculate frequency distribution
    import numpy as np
    hist, edges = np.histogram(submission_times, bins=bins)

    # Prepare data for the chart (bin labels and frequency values)
    bin_labels = [f"{edges[i]}–{edges[i+1]}" for i in range(len(edges)-1)]
    frequencies = hist.tolist()

    # Render the template with all necessary context
    return render_template("QuestionResults.html", question=question, user_score=user_score, bin_labels=bin_labels, frequencies=frequencies)




@app.route('/QuestionAnswer', methods=['GET', 'POST'])
@login_required
def QuestionAnswer():
    if request.method == 'POST':
        question_id = request.form.get('question_id', type=int)
        code = request.form.get('code')
        runtime_sec = request.form.get('runtime_sec', type=int)

        # I'll do real evaluations later when I figure out how to get the testing working for now they're just placeholders (except lines of code)
        passed = True  
        tests_run = 3
        lines_of_code = code.count('\n') + 1 if code else 0

        submission = Submission(
            user_id=current_user.id,
            question_id=question_id,
            code=code,
            passed=passed,
            runtime_sec=runtime_sec,
            lines_of_code=lines_of_code,
            tests_run=tests_run
        )
        db.session.add(submission)
        db.session.commit()

        return redirect(url_for('QuestionStatPage.html', id=question_id))
    
    # puts information on the page
    question_id = request.args.get('id', type=int)
    if not question_id:
        return "No question ID provided", 400
    question = Question.query.get_or_404(question_id)
    return render_template("QuestionAnswer.html", question=question)

