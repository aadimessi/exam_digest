import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, addDoc, getDocs, deleteDoc, doc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const firebaseConfig = {
    apiKey: "AIzaSyAdvbkZaLSJsJlaAkURHACbt2cJtemBa5U",
    authDomain: "quiz-app-e8d1d.firebaseapp.com",
    projectId: "quiz-app-e8d1d",
    storageBucket: "quiz-app-e8d1d.appspot.com",
    messagingSenderId: "421848385039",
    appId: "1:421848385039:web:cbb560cf9d839752ce457a"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function addQuestion() {
    const questionText = document.getElementById('question-input').value.trim();
    const options = [
        document.getElementById('option1').value.trim(),
        document.getElementById('option2').value.trim(),
        document.getElementById('option3').value.trim(),
        document.getElementById('option4').value.trim()
    ];
    const correctAnswerIndex = document.getElementById('correct-answer').value;
    const correctAnswer = options[correctAnswerIndex]; 
    const saveButton = document.getElementById("saveQuestionBtn");

    const examId = document.getElementById("examSelect").value;

    if (!questionText || options.includes("")) {
        alert("⚠️ Please fill in all fields!");
        return;
    }

    saveButton.disabled = true; 

    try {
        await addDoc(collection(db, "quizQuestions"), {
            question: questionText,
            options: options,
            correctAnswer: correctAnswer,
            examId: examId   
        });

        alert("✅ Question added successfully!");
        clearQuestionFields();
        displayQuestions(); 
    } catch (error) {
        console.error("❌ Error adding question:", error);
        alert("Failed to save question.");
    } finally {
        saveButton.disabled = false; 
    }
}

async function displayQuestions() {
    const questionList = document.getElementById("question-list");
    questionList.innerHTML = "Loading...";

    try {
        const querySnapshot = await getDocs(collection(db, "quizQuestions"));
        questionList.innerHTML = "";

        querySnapshot.forEach((docSnap) => {
            const questionData = docSnap.data();
            const questionId = docSnap.id;
            let li = document.createElement("li");
            li.innerHTML = `${questionData.question} <button onclick="deleteQuestion('${questionId}')">❌ Delete</button>`;
            questionList.appendChild(li);
        });
    } catch (error) {
        console.error("❌ Error loading questions:", error);
        questionList.innerHTML = "Failed to load questions.";
    }
}

async function addStudent() {
    const studentName = document.getElementById('student-name').value.trim();
    const studentID = document.getElementById('student-id').value.trim();
    const saveStudentBtn = document.getElementById("saveStudentBtn");

    if (!studentName || !studentID) {
        alert("⚠️ Please enter both student name and ID!");
        return;
    }

    saveStudentBtn.disabled = true; 

    try {
        await addDoc(collection(db, "students"), {
            name: studentName,
            id: studentID
        });

        alert("✅ Student added successfully!");
        clearStudentFields();
        displayStudents(); 
    } catch (error) {
        console.error("❌ Error adding student:", error);
        alert("Failed to add student.");
    } finally {
        saveStudentBtn.disabled = false; 
    }
}

async function displayStudents() {
    const studentList = document.getElementById("student-list");
    studentList.innerHTML = "Loading...";

    try {
        const querySnapshot = await getDocs(collection(db, "students"));
        studentList.innerHTML = "";

        querySnapshot.forEach((docSnap) => {
            const studentData = docSnap.data();
            const studentId = docSnap.id;
            let li = document.createElement("li");
            li.innerHTML = `${studentData.name} (ID: ${studentData.id}) <button onclick="deleteStudent('${studentId}')">❌ Delete</button>`;
            studentList.appendChild(li);
        });
    } catch (error) {
        console.error("❌ Error loading students:", error);
        studentList.innerHTML = "Failed to load students.";
    }
}

async function deleteStudent(id) {
    if (!confirm("Are you sure you want to delete this student?")) return;

    try {
        await deleteDoc(doc(db, "students", id));
        alert("🗑️ Student deleted successfully!");
        displayStudents(); 
    } catch (error) {
        console.error("❌ Error deleting student:", error);
        alert("Failed to delete student.");
    }
}

function clearQuestionFields() {
    document.getElementById('question-input').value = "";
    document.getElementById('option1').value = "";
    document.getElementById('option2').value = "";
    document.getElementById('option3').value = "";
    document.getElementById('option4').value = "";
    document.getElementById('correct-answer').selectedIndex = 0;
}

function clearStudentFields() {
    document.getElementById('student-name').value = "";
    document.getElementById('student-id').value = "";
}

document.getElementById("saveQuestionBtn").addEventListener("click", addQuestion);
document.getElementById("saveStudentBtn").addEventListener("click", addStudent);

window.onload = function () {
    displayQuestions();
    displayStudents();
};
