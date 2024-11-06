const createError = require("http-errors");
const express = require("express");
const path = require("path");
const app = express();
const mysql = require("mysql2/promise");
const port = 3000;

const dbConfig = {
  host: 'mariadb-service',
  user: 'ubuntu',
  password: 'ubuntu',
  database: 'ubuntu'
};

// EJS 설정
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "public", "views"));

// 정적 파일 설정

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, "public")));

async function getDbConnection() {
  return await mysql.createConnection(dbConfig);
}

// 라우트 파일 불러오기
const indexRouter = require('./public/index');

// 라우트 미들웨어 설정
app.use("/", indexRouter);

app.get('/visitor-detail', async (req, res) => {
  const token = req.query.token;

  if (!token) {
    return res.status(400).send("Token is required");
  }

  try {
    const db = await getDbConnection();
    const [rows] = await db.execute('SELECT * FROM users WHERE token = ?', [token]);

    if (rows.length === 0) {
      return res.status(404).send("Visitor not found");
    }

    const visitor = rows[0];
    res.render('visitor_detail', { visitor });
  } catch (error) {
    console.error('Error fetching visitor:', error.message);
    res.status(500).send("Server error");
  }
});

app.get('/admin-dashboard', async (req, res) => {
  try {
    const db = await getDbConnection();
    const [pendingVisitors] = await db.execute('SELECT * FROM users WHERE status = ?', ['PENDING']);
    res.render('admin_dashboard', { pending_visitors: pendingVisitors });
  } catch (error) {
    console.error("Error fetching pending visitors:", error);
    res.status(500).send("서버 오류 발생");
  }
});

app.post('/admin-login', (req, res) => {
    const { username, password } = req.body;

    console.log(`Incoming login attempt - Username: ${username}`);

    if (username === 'admin' && password === 'admin') {
        res.json({
            success: true,
            message: '로그인 성공',
            redirect_url: '/admin-dashboard'
        });
    } else {
        res.status(401).json({
            success: false,
            message: '로그인 실패: 아이디 또는 비밀번호가 잘못되었습니다.'
        });
    }
});

app.use(function (req, res, next) {
  next(createError(404));
});

// 서버 시작
app.listen(port, '0.0.0.0',() => {
  console.log(`frontend server on port ${port}`);
});

module.exports = app;
