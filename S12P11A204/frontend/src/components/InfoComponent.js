import React, { useEffect, useState } from 'react';
import '../styles/Info.css'
import genesisImage from '../assets/genesisman.png'

const InfoComponent = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="info-container">
      <div className="info-overlay">
        <div className='info-text-sub'>
          <p>Since OKDK(OK, DRAIN KEEPER),</p>
          <p>a rain gauge inspection and management self-driving robot</p>
          <p>aimed at preventing flooding in the city,</p>
          <p>there is no more Genesis man.</p>
        </div>
        <div className='info-text-main'>
          <p className="info-text-kr">도심 침수 방지용 자율주행 로봇</p>
          <p className="info-title">OKDK</p>
          <p className='sub-title'>OK, DRAIN KEEPER</p>
        </div>
      </div>
    </div>
  );
};

export default InfoComponent;
