const express = require("express");
const router = express.Router();
const axios = require("axios");
const mysql = require("mysql2/promise");
const path = require("path");
const adminServiceUrl = "http://admin-service:8000";
const visitorServiceUrl = "http://visitor-service:8050";

// 데이터베이스 연결 설정
const dbConfig = {
  host: 'mariadb-service',
  user: 'ubuntu',
  password: 'ubuntu',
  database: 'ubuntu'
};

// 데이터베이스 연결 함수
async function getDbConnection() {
  return await mysql.createConnection(dbConfig);
}

/* GET home page. */
router.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "/views/index.html"));
});

// 관리자 로그인 처리 및 대시보드 데이터 가져오기
router.post('/admin-dashboard', async (req, res) => {
  const { username } = req.body;

  console.log(`Incoming login attempt - Username: ${username}`);

  try {
    // FastAPI에서 대시보드 데이터를 가져옴
    const response = await axios.get(`${adminServiceUrl}/admin/admin-dashboard`);
    const data = response.data;

    console.log("Fetched data from FastAPI:", data);

    // EJS 템플릿을 렌더링하면서 데이터를 전달
    res.render("admin_dashboard", {
      pending_visitors: data.pending_visitors
    });

  } catch (error) {
    console.error("Error fetching data from FastAPI:", error);
    res.status(500).send("Error fetching admin dashboard data");
  }
});

// 방문자 등록 페이지 라우트
router.get("/visitor-register", (req, res) => {
  res.render("visitor_register");
});

// 방문자 등록 처리 라우트
router.post("/visitor-register", async (req, res) => {
  const visitorData = {
    name: req.body.name,
    email: req.body.email,
    phone: req.body.phone,
    ob: req.body.ob,
    aname: req.body.aname,
    job: req.body.job,
  };

  try {
    const params = new URLSearchParams(visitorData);

    const response = await axios.post(`${visitorServiceUrl}/visitor/visitor-register`, params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    if (response.status === 200) {
      res.redirect("/?registered=true");
    } else {
      res.status(500).send("Error registering visitor.");
    }
  } catch (error) {
    console.error("Error:", error);
    res.status(500).send("Error registering visitor.");
  }
});

// 방문자 대시보드 라우트
router.get("/visitor-dashboard", async (req, res) => {
  try {
    const response = await axios.get(`${visitorServiceUrl}/visitor/visitor-dashboard`);
    const visitors = response.data.visitors;

    // 상태 번역 객체
    const statusTranslations = {
      "PENDING": "대기 중",
      "APPROVED": "승인됨",
      "REJECTED": "거부됨",
      "EXIT": "퇴입 완료"
    };

    // EJS 템플릿에 데이터 전달
    res.render("visitor_dashboard", { visitors, statusTranslations });
  } catch (error) {
    console.error("방문자 데이터를 가져오는 중 오류:", error);
    res.status(500).send("방문자 데이터를 가져오는 중 오류가 발생했습니다.");
  }
});

// 방문자 목록 페이지 라우트
router.get("/visitor-list", async (req, res) => {
  try {
    const response = await axios.get(`${visitorServiceUrl}/visitor/visitor-dashboard`);
    res.render("visitor_list", { visitors: response.data.visitors });
  } catch (error) {
    console.error("Error fetching visitor data:", error);
    res.status(500).send("Error fetching visitor data.");
  }
});

// 관리자 대시보드 라우트 (데이터베이스에서 직접 조회)
router.get('/admin-dashboard', async (req, res) => {
  let db;
  try {
    db = await getDbConnection();
    const [pendingVisitors] = await db.execute('SELECT * FROM users WHERE status = ?', ['PENDING']);
    res.render('admin_dashboard', { pending_visitors: pendingVisitors });
  } catch (error) {
    console.error("Error fetching pending visitors:", error);
    res.status(500).send("서버 오류 발생");
  } finally {
    if (db) await db.end();
  }
});

// 승인 및 거절 처리 라우트
router.post("/admin-approve/:visitorId", async (req, res) => {
  const visitorId = req.params.visitorId;

  try {
    // FastAPI에 승인 요청 보내기
    const response = await axios.post(`${adminServiceUrl}/admin/admin-approve/${visitorId}`);
    if (response.data.success) {
      res.redirect('/admin-dashboard');
    } else {
      res.status(500).send(response.data.message);
    }
  } catch (error) {
    console.error("Error approving visitor:", error);
    res.status(500).send("방문자 승인 중 오류 발생");
  }
});

router.post("/admin-reject/:visitorId", async (req, res) => {
  const visitorId = req.params.visitorId;

  try {
    // FastAPI에 거절 요청 보내기
    const response = await axios.post(`${adminServiceUrl}/admin/admin-reject/${visitorId}`);
    if (response.data.success) {
      res.redirect('/admin-dashboard');
    } else {
      res.status(500).send(response.data.message);
    }
  } catch (error) {
    console.error("Error rejecting visitor:", error);
    res.status(500).send("방문자 거절 중 오류 발생");
  }
});

// 방문자 통계 페이지 라우트
router.get("/statistics", async (req, res) => {
  try {
    const response = await axios.get(`${adminServiceUrl}/admin/statistics`);
    const data = response.data;

    console.log("Fetched data:", data);

    // EJS 템플릿에 데이터 전달
    res.render("statistics", {
      total_visitors: data.total_visitors,
      avg_visit_duration: data.avg_visit_duration,
      weekday_graph: data.weekday_graph,
      hour_graph: data.hour_graph
    });
  } catch (error) {
    console.error("Error fetching data from FastAPI:", error);
    res.status(500).send("Error fetching statistics data");
  }
});

router.post("/admin-exit/:visitorId", async (req, res) => {
  const visitorId = req.params.visitorId;

  try {
    // FastAPI에 퇴입 요청 보내기
    const response = await axios.post(`${adminServiceUrl}/admin/exit/${visitorId}`, {
      admin_id: 1
    });

    if (response.data.success) {
      res.status(200).json({ success: true, message: "퇴입 완료" });
    } else {
      res.status(500).json({ success: false, message: response.data.message });
    }
  } catch (error) {
    console.error("Error during exit process:", error);
    res.status(500).json({ success: false, message: "퇴입 처리 중 오류 발생" });
  }
});


module.exports = router;
