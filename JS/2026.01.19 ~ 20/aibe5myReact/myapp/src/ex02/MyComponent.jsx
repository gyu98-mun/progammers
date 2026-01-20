import React from 'react';

function MyComponent(props) {
    return (
        <div>
            안녕하세요, 제 이름은 {props.name}입니다. <br/>
            나이는 {props.age}살입니다.
            견종은 {props.children}입니다.
        </div>
    );
}

export default MyComponent;