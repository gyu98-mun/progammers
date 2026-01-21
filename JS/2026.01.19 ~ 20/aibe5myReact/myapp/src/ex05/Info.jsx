import React, {useState} from 'react';

const Info = () => {
    const [inputs, setInputs] = useState({
        name: '',
        nickname: '',
        email: '',
        phone: '',
        comment: ''
    });
    const [DisplayData, setDisplayData] = useState({
        name: '',
        nickname: '',
        email: '',
        phone: '',
        comment: ''
    });
    const onChangeName = (e) => {
        setInputs({...inputs, name: e.target.value});
    }
    const onChangeNickname = (e) => {
        setInputs({...inputs, nickname: e.target.value});
    }
    const onChangeEmail = (e) => {
        setInputs({...inputs, email: e.target.value});
    }
    const onChangePhone = (e) => {
        setInputs({...inputs, phone: e.target.value});
    }
    const onChangeComment = (e) => {
        setInputs({...inputs, comment: e.target.value});
    }
    const onClickReset = () => {
        setInputs({
            name: '',
            nickname: '',
            email: '',
            phone: '',
            comment: ''
        });
    }   
    const onClickInput = () => {
        setDisplayData({
            name: inputs.name,
            nickname: inputs.nickname,
            email: inputs.email,
            phone: inputs.phone,
            comment: inputs.comment
        });
    }
    return (
        <div>
            <div>
                <input name="name" value={inputs.name} onChange={onChangeName} placeholder='이름' />
                <input name="nickname" value={inputs.nickname} onChange={onChangeNickname} placeholder='닉네임' />
                <input name="email" value={inputs.email} onChange={onChangeEmail} placeholder='이메일' />
                <input name="phone" value={inputs.phone} onChange={onChangePhone} placeholder='전화번호' />
                <input name="comment" value={inputs.comment} onChange={onChangeComment} placeholder='댓글' />
                <button onClick={onClickReset}>초기화</button> <br/>
                <button onClick={onClickInput}>입력</button>
            </div>
            <div>
                <div>
                    <b>이름:</b> {DisplayData.name}
                </div>
                <div>
                    <b>닉네임:</b> {DisplayData.nickname}
                </div>
                <div>
                    <b>이메일:</b> {DisplayData.email}
                </div>
                <div>
                    <b>전화번호:</b> {DisplayData.phone}
                </div>
                <div>
                    <b>댓글:</b> {DisplayData.comment}
                </div>
            </div>
        </div>
    );
};

export default Info;