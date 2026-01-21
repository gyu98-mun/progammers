import React, { useState } from 'react';

const Say = () => {
    const [message, setMessage] = useState('');
    const onclickEnter = () => setMessage('안녕하세요!');
    const onclickLeave = () => setMessage('안녕히가세요!');
    const [color, setColor] = useState('black');
    const onclickReset = () => {setMessage(''); setColor('black');};
    return (
        <div>
            <button onClick={onclickEnter}>입장</button>
            <button onClick={onclickLeave}>퇴장</button>
            <button onClick={onclickReset}>초기화</button>            
            <h1 style={{color}}>{message}</h1>
            <button style={{color : "red"}} onClick={() => setColor('red')}>빨간색</button>
            <button style={{color : "green"}} onClick={() => setColor('green')}>초록색</button>
            <button style={{color : "blue"}} onClick={() => setColor('blue')}>파란색</button>
            <button style={{color : "black"}} onClick={() => setColor('black')}>검은색</button>
        </div>
    );
};

export default Say;