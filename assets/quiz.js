/* quiz.js — shared retrieval-practice widget for the Claude Architect course.
 *
 * Usage in any lesson:
 *   <div class="quiz">
 *     <script type="application/json">
 *       [{"q": "...", "answers": ["A","B","C","D"], "correct": 0, "why": "...", "multi": false}]
 *     </script>
 *   </div>
 *   <script src="../assets/quiz.js"></script>
 *
 * Features:
 *   - Answers are SHUFFLED on every render (no position-based guessing)
 *   - Single-select (default): click to answer, instant feedback
 *   - Multi-select ("multi": true): checkboxes, all must match to score
 *   - Score tracking, retake, explanation after each answer
 */
(function () {
  "use strict";

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
    }
    return a;
  }

  function initQuiz(container) {
    var dataScript = container.querySelector('script[type="application/json"]');
    if (!dataScript) return;
    var questions;
    try { questions = JSON.parse(dataScript.textContent); } catch (e) { return; }
    dataScript.parentNode.removeChild(dataScript);
    if (!questions.length) return;

    var score = 0;

    var header = el("div", "quiz-header");
    header.appendChild(el("span", "quiz-title", "Retrieval practice"));
    var counter = el("span", "quiz-count", "");
    header.appendChild(counter);
    container.appendChild(header);

    var stage = el("div", "quiz-stage");
    container.appendChild(stage);

    function showQuestion(i) {
      stage.innerHTML = "";
      counter.textContent = (i + 1) + " / " + questions.length;
      var item = questions[i];
      var isMulti = item.multi === true;
      var correctSet = isMulti ? item.correct : [item.correct];

      // Shuffle answers, track the new indices of correct ones
      var indexed = item.answers.map(function(a, idx) { return {text: a, orig: idx}; });
      var shuffled = shuffle(indexed);
      var newCorrect = shuffled.map(function(pair, newIdx) {
        return correctSet.indexOf(pair.orig) >= 0 ? newIdx : -1;
      }).filter(function(x) { return x >= 0; });

      stage.appendChild(el("div", "quiz-q", item.q));
      if (isMulti) {
        stage.appendChild(el("div", "quiz-hint", "Select all that apply (" + newCorrect.length + " correct)"));
      }

      var options = el("div", "quiz-options");
      var why = null;
      var buttons = [];
      var selected = [];

      shuffled.forEach(function(pair, idx) {
        var btn = el("button", "quiz-option", pair.text);
        btn.type = "button";
        btn.addEventListener("click", function() {
          if (isMulti) {
            btn.classList.toggle("multi-selected");
            var pos = selected.indexOf(idx);
            if (pos >= 0) selected.splice(pos, 1); else selected.push(idx);
            var checkBtn = stage.querySelector(".quiz-btn");
            if (checkBtn) checkBtn.disabled = selected.length === 0;
          } else {
            buttons.forEach(function(b) { b.disabled = true; });
            var isRight = newCorrect.indexOf(idx) >= 0;
            btn.classList.add(isRight ? "is-correct" : "is-wrong");
            if (!isRight) {
              buttons[newCorrect[0]].classList.add("is-reveal", "is-correct");
            }
            if (isRight) score++;
            showWhy(isRight);
          }
        });
        buttons.push(btn);
        options.appendChild(btn);
      });
      stage.appendChild(options);

      if (isMulti) {
        var actions = el("div", "quiz-actions");
        var checkBtn = el("button", "quiz-btn", "Check answer");
        checkBtn.type = "button";
        checkBtn.disabled = true;
        checkBtn.addEventListener("click", function() {
          buttons.forEach(function(b) { b.disabled = true; });
          var allRight = true;
          selected.forEach(function(idx) {
            var isRight = newCorrect.indexOf(idx) >= 0;
            buttons[idx].classList.add(isRight ? "is-correct" : "is-wrong");
            if (!isRight) allRight = false;
          });
          newCorrect.forEach(function(idx) {
            if (selected.indexOf(idx) < 0) {
              buttons[idx].classList.add("is-reveal", "is-correct");
              allRight = false;
            }
          });
          if (allRight) score++;
          showWhy(allRight);
        });
        actions.appendChild(checkBtn);
        stage.appendChild(actions);
      }

      function showWhy(isCorrect) {
        why = el("div", "quiz-why " + (isCorrect ? "correct" : "wrong"));
        var label = el("b", null, isCorrect ? "Correct. " : "Not quite. ");
        why.appendChild(label);
        why.appendChild(document.createTextNode(item.why));
        stage.appendChild(why);
        var nextBtn = stage.querySelector(".quiz-btn") || el("button", "quiz-btn", "Next question");
        nextBtn.textContent = i + 1 < questions.length ? "Next question" : "See score";
        nextBtn.disabled = false;
        nextBtn.onclick = function() {
          if (i + 1 < questions.length) showQuestion(i + 1);
          else showResults();
        };
        if (!stage.querySelector(".quiz-btn")) {
          var act = el("div", "quiz-actions");
          act.appendChild(nextBtn);
          stage.appendChild(act);
        }
      }
    }

    function showResults() {
      stage.innerHTML = "";
      counter.textContent = "done";
      var pct = Math.round((score / questions.length) * 100);
      var message = pct === 100 ? "Perfect — stored, not just fluent." :
        pct >= 75 ? "Solid. Revisit the ones you missed." :
        pct >= 50 ? "Halfway — reread the section, then retake." :
        "Worth rereading the lesson, then trying again.";
      var scoreLine = el("div", "quiz-score");
      var strong = el("strong", null, score + " / " + questions.length);
      scoreLine.appendChild(strong);
      scoreLine.appendChild(document.createTextNode(" — " + message));
      stage.appendChild(scoreLine);
      var actions = el("div", "quiz-actions");
      var retake = el("button", "quiz-btn", "Retake (reshuffled)");
      retake.type = "button";
      retake.addEventListener("click", function() { score = 0; showQuestion(0); });
      actions.appendChild(retake);
      stage.appendChild(actions);
    }

    showQuestion(0);
  }

  document.addEventListener("DOMContentLoaded", function() {
    var quizzes = document.querySelectorAll(".quiz");
    for (var i = 0; i < quizzes.length; i++) initQuiz(quizzes[i]);
  });
})();
