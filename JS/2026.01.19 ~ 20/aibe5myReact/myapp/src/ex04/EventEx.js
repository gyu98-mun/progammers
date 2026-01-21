import React, {useState} from 'react';

const EventEx = () => {
    const [form, setForm] = useState({
        username: '',
        message: ''
    });
    const [submittedText, setSubmittedText] = useState('');
    const { username, message } = form;
    const onChange = e => {
        const nextForm = {
            ...form,
            [e.target.name]: e.target.value
        };
        setForm(nextForm);
    };
    const onClick = () => {
        setSubmittedText(`${username}: ${message}`); 
        alert(`${username}: ${message}`);
        setForm({
            username: '',
            message: ''
        });
    };
    const onKeyPress = e => {
        if (e.key === 'Enter') {
            onClick();
        }
    };
    return (
        <>
            <div>
                <h1>이벤트 연습</h1>
                <input
                    type="text"
                    name="username"
                    placeholder="유저명"
                    value={username}
                    onChange={onChange}
                />
                <input
                    type="text"
                    name="message"
                    placeholder="아무거나 입력해보세요"
                    value={message}
                    onChange={onChange}
                    onKeyPress={onKeyPress}
                />
                <button onClick={onClick}>확인</button>
            </div>
            <div>
                <h2>{submittedText}</h2>
            </div>
        </>
    );
}

export default EventEx;