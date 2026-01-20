import React from 'react';
import Books from './Book';

function Library(props) {
    return (
        <div>
            <Books name="코딩 좀 아는 사람" numOfPage={312} />
            <Books name="Java 언어로 배우는 디자인 패턴 입문" numOfPage={560} />
            <Books name="계속 가봅시다 남는 게 체력인데" numOfPage={284} />
        </div>
    );
}

export default Library;