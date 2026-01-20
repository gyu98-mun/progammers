import { GoogleGenerativeAI } from "@google/generative-ai";
import * as dotenv from "dotenv";
import express from "express";
import path from "path";
import { fileURLToPath } from 'url';

// 1. [VALUE DECLARATION]
dotenv.config();
const app = express();
const PORT = 3000;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 사용자 요청에 따른 모델명 설정
const TARGET_MODEL = "gemini-2.5-flash"; 

const API_KEYS = [
    process.env.GEMINI_API_KEY_1,
    process.env.GEMINI_API_KEY_2,
    process.env.GEMINI_API_KEY_3,
    process.env.GEMINI_API_KEY_4,
    process.env.GEMINI_API_KEY_5
];
let currentKeyIndex = 0;

app.use(express.json());
app.use(express.static(__dirname));

// ---------------------------------------------------------

// 2. [MAIN LOOP / ROUTES]
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "AiChatbot.html"));
});

app.post("/chat", async (req, res) => {
    const userMessage = req.body.message;
    console.log(`[시스템] 2.5 Flash 모델로 시도 중...`);
    
    try {
        const aiResponse = await getAiResponseWithFailover(userMessage);
        res.json({ reply: aiResponse });
    } catch (criticalError) {
        console.error("Critical Server Error:", criticalError);
        res.status(500).json({ reply: "서버 내부 로직 오류가 발생했습니다." });
    }
});

app.listen(PORT, () => console.log(`http://localhost:${PORT}`));

// ---------------------------------------------------------

// 3. [FUNCTION DECLARATION]
async function getAiResponseWithFailover(prompt) {
    for (let i = 0; i < API_KEYS.length; i++) {
        const activeKey = API_KEYS[currentKeyIndex];
        const result = await callGeminiApi(activeKey, prompt);

        if (!result.isError) return result.text;

        console.warn(`${currentKeyIndex + 1}번 키 실패. 사유: ${result.text}`);
        currentKeyIndex = (currentKeyIndex + 1) % API_KEYS.length;
    }
    return "모든 API 키가 실패했습니다.";
}

async function callGeminiApi(key, text) {
    try {
        const genAI = new GoogleGenerativeAI(key);
        // 모델명 2.5 Flash 적용
        const model = genAI.getGenerativeModel({ model: TARGET_MODEL });
        const result = await model.generateContent(text);
        return { isError: false, text: result.response.text() };
    } catch (error) {
        return { isError: true, text: error.message };
    }
}