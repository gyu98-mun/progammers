import React, {useState} from 'react';

function Counter(props) {
    const [count, setCount] = useState(0);
    return (
        <div>
            <p>현재 카운터 값은<b>{count}</b>입니다.</p>
            <button onClick={() => setCount(count + 1)}>+1</button>
            <button onClick={() => setCount(count - 1)}>-1</button>
            <button onClick={() => setCount(0)}>react</button>
        </div>
    );
}

export default Counter;