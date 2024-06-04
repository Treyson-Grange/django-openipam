import React from "react";
//@ts-ignore
import NotFound from "../../public/NotFound.png";
const screenWidth = window.screen.width;
const screenHeight = window.screen.height;
export const NotFoundPage = () => {
  return (
    <div className={`w-[${screenWidth}px] h-[${screenHeight - 100}px]`}>
      <div className="font-bold text-4xl w-[80%] m-auto text-center mt-20">
        404 NOT FOUND
      </div>
      <img src={NotFound} className="w-[40%] h-[40%] m-auto image-full" />
      <div className="font-bold text-2xl w-[80%] m-auto">
        You thought this mission to the moon would be a quick six month thing.
        Your neighbor offered to look after your dog. Your high school math
        teacher was impressed. He once said you wouldn’t amount to anything. You
        sure showed him. But now here you are, fifty feet from your spaceship
        with no way to get back. Your dog will be so sad. Your math teacher will
        be so smug. Pretty devastating.
      </div>
    </div>
  );
};
