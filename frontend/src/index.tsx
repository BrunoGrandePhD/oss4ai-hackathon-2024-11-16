import { FC } from "react";
import ReactDOM from "react-dom";
import "./style.css";
import Homepage from "./components/Homepage";

const App: FC = () => {
  return (
    <div>
      <Homepage/>
    </div>
  );
};

const rootElement = document.getElementById("root");
ReactDOM.render(<App />, rootElement);
