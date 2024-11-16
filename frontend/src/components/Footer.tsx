import React from 'react';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

const Footer: React.FC = () => {
  return (
    <footer className="bg-light py-3 mt-auto">
      <Container>
        <p className="text-center mb-0"> Santina Lin</p>
      </Container>
    </footer>
  );
};

export default Footer;
